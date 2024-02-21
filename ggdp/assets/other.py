import pandas as pd
import requests
from dagster import AssetIn, Backoff, RetryPolicy, asset
from tenacity import retry, wait_exponential, stop_after_attempt

from ..resources import DuneResource, CovalentAPIResource


@asset(
    retry_policy=RetryPolicy(max_retries=3, delay=0.2, backoff=Backoff.EXPONENTIAL),
    ins={"raw_allo_rounds": AssetIn("raw_allo_rounds")},
)
def raw_chain_metadata(raw_allo_rounds: pd.DataFrame) -> pd.DataFrame:
    """
    Metadata for chains on which Gitcoin indexer registered at least one round. Source: `chainid.network/chains.json`
    """
    interesting_chains = raw_allo_rounds.chainId.unique()

    df = pd.read_json("https://chainid.network/chains.json")
    df = df.convert_dtypes()
    df.chainId = df.chainId.astype(str)
    filtered_df = df[df.chainId.isin(interesting_chains)]

    return filtered_df


@asset(compute_kind="API")
def dune_allo_deployments(
    dune: DuneResource, raw_allo_deployments: pd.DataFrame
) -> None:
    """
    Uploads allo deployments to Dune.
    """
    dune.upload_csv(raw_allo_deployments, "allo_contract_deployments")


@asset(compute_kind="API")
def ethereum_project_registry_tx(covalent_api: CovalentAPIResource):
    """
    All Ethereum mainnet transactions targeting project registry, from Covalent
    """

    all_tx = covalent_api.fetch_all_tx_for_address(
        "eth-mainnet", "0x03506eD3f57892C85DB20C36846e9c808aFe9ef4"
    )

    dataframes = [pd.DataFrame(data.get("items")) for data in all_tx]
    combined_df = pd.concat(dataframes, ignore_index=True)

    return combined_df


@retry(
    stop=stop_after_attempt(8),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
def fetch_giveth_projects(url, query):
    all_projects = []
    skip = 0

    while True:
        response = requests.post(
            url, json={"query": query, "variables": {"skip": skip}}
        )
        data = response.json()

        projects = data["data"]["allProjects"]["projects"]
        all_projects.extend(projects)
        skip += 50

        if skip >= data["data"]["allProjects"]["totalCount"]:
            break
    return all_projects


@asset
def raw_giveth_projects():
    url = "https://mainnet.serve.giveth.io/graphql"
    query = """
        query GetProjects($skip: Int!) {
            allProjects(take: 50, limit: 50, skip: $skip) {
                totalCount
                projects {
                    title
                    totalDonations
                    totalTraceDonations
                }
            }
        }
    """

    all_projects = fetch_giveth_projects(url, query)
    giveth = pd.DataFrame(all_projects)
    giveth.convert_dtypes()
    return giveth


@asset
def raw_discourse_categories():
    """
    Listing of categories from "Discourse" of various communities.

    Use 'source' column to group categories by Discourse instance.
    """
    forums = {
        "Gitcoin": "https://gov.gitcoin.co",
        "Giveth": "https://forum.giveth.io",
        "Arbitrum": "https://forum.arbitrum.foundation",
        "Optimism": "https://gov.optimism.io/",
    }

    data = []
    for community, forum_address in forums.items():
        catalog = pd.read_json(f"{forum_address}/categories.json")
        catalog = catalog["category_list"]["categories"]
        for category in catalog:
            category["source"] = community
        data.extend(catalog)

    discourse_df = pd.DataFrame(data)
    discourse_df = discourse_df.convert_dtypes()
    return discourse_df


@asset
def raw_gitcoin_passport_scores() -> pd.DataFrame:
    file_url = "https://indexer-production.fly.dev/data/passport_scores.json"
    df = pd.read_json(file_url)
    df = df.drop(columns=["error", "stamp_scores"])

    df["last_score_timestamp"] = pd.to_datetime(
        df["last_score_timestamp"], errors="coerce"
    )

    return df[df["address"].str.startswith("0x")]
