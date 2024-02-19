import json

import pandas as pd
import requests
from retry import retry
from dagster import asset
from fsspec.implementations.http import HTTPFileSystem

from .resources import DuneResource, CovalentAPIResource

ALLO_INDEXER_URL = "https://indexer-production.fly.dev/data"
CHAIN_METADATA_URL = "https://chainid.network/chains.json"
GIVETH_GQL_ENDPOINT = "https://mainnet.serve.giveth.io/graphql"


def chain_file_aggregator(json_name):
    fs = HTTPFileSystem(simple_links=True)
    paths = fs.ls(ALLO_INDEXER_URL)
    paths = [path["name"] for path in paths if path["name"].split("/")[-1].isdigit()]
    df = pd.DataFrame()
    for path in paths:
        chain_id = int(path.split("/")[-1])
        try:
            df_chain = pd.read_json(f"{path}/{json_name}")
            df_chain["chainId"] = str(chain_id)
        except Exception as e:
            print(f"Error reading {path}/{json_name}")
            print(f"Error: {e}")
            df_chain = pd.DataFrame()
            continue
        df = pd.concat([df, df_chain])
    return df


@retry(tries=8, delay=2, backoff=2, max_delay=10)
def read_json_with_retry(json_path):
    response = requests.get(json_path, timeout=10)
    response.raise_for_status()
    return pd.read_json(response.text)


@retry(tries=8, delay=2, backoff=2, max_delay=10)
def read_parquet_with_retry(path):
    return pd.read_parquet(path)


def round_file_aggregator(json_name):
    fs = HTTPFileSystem(simple_links=True)
    paths = fs.ls(ALLO_INDEXER_URL)
    paths = [path["name"] for path in paths if path["name"].split("/")[-1].isdigit()]

    df = pd.DataFrame()

    for path in paths:
        chain_id = int(path.split("/")[-1])

        try:
            chain_rounds = fs.ls(f"{path}/rounds/")
        except Exception as e:
            print(f"Error reading {path}/rounds/")
            print(f"Error: {e}")
            continue

        chain_rounds = [
            round["name"]
            for round in chain_rounds
            if round["name"].split("/")[-1].startswith("0x")
        ]

        for round in chain_rounds:
            round_id = round.split("/")[-1]
            try:
                df_round = read_json_with_retry(f"{round}/{json_name}")
            except Exception as e:
                print(f"Error reading {round}/{json_name}")
                print(f"Error: {e}")
                continue
            df_round["chainId"] = str(chain_id)
            df_round["roundId"] = str(round_id)
            df = pd.concat([df, df_round])

    df = df.convert_dtypes()

    return df


@asset
def raw_passport_scores() -> pd.DataFrame:
    file_url = f"{ALLO_INDEXER_URL}/passport_scores.json"
    df = pd.read_json(file_url)
    df = df.drop(columns=["error", "stamp_scores"])
    df["last_score_timestamp"] = pd.to_datetime(
        df["last_score_timestamp"], errors="coerce"
    )

    return df[df["address"].str.startswith("0x")]


@asset
def raw_projects() -> pd.DataFrame:
    projects = chain_file_aggregator("projects.json")
    projects["metadata"] = projects["metadata"].apply(json.dumps)
    return projects


@asset
def raw_prices() -> pd.DataFrame:
    return chain_file_aggregator("prices.json")


@asset
def raw_rounds() -> pd.DataFrame:
    rounds = chain_file_aggregator("rounds.json")
    rounds["metadata"] = rounds["metadata"].apply(json.dumps)
    return rounds


@asset
def raw_round_votes() -> pd.DataFrame:
    return round_file_aggregator("votes.json")


@asset
def raw_round_applications() -> pd.DataFrame:
    applications = round_file_aggregator("applications.json")
    applications["metadata"] = applications["metadata"].apply(json.dumps)
    applications["roundId"] = '"' + applications["roundId"] + '"'
    applications = applications.convert_dtypes()
    return applications


@asset
def raw_round_contributors() -> pd.DataFrame:
    df = round_file_aggregator("contributors.json")
    df["roundId"] = '"' + df["roundId"] + '"'
    return df


@asset
def raw_chain_metadata(raw_rounds: pd.DataFrame) -> pd.DataFrame:
    """
    Metadata for chains on which Gitcoin indexer registered at least one round. Source: `chainid.network/chains.json`
    """
    interesting_chains = raw_rounds.chainId.unique()

    try:
        chain_metadata = read_json_with_retry(CHAIN_METADATA_URL)
    except Exception as e:
        print(f"Error fetching chain list from {CHAIN_METADATA_URL}: {e}")
        raise

    df = pd.DataFrame(chain_metadata)
    df = df.convert_dtypes()
    df.chainId = df.chainId.astype(
        str
    )  # Save as VARCHAR to stay consistent with other models.
    filtered_df = df[df.chainId.isin(interesting_chains)]

    return filtered_df


@asset
def raw_allo_deployments() -> pd.DataFrame:
    """
    Deployment address for all official allo contract deployments by Allo team, collected 07.01.24

    Canonical source: https://github.com/allo-protocol/allo-contracts/blob/main/docs/CHAINS.md
    Ingestion logic: https://gist.github.com/DistributedDoge/57e39c3e5cc207fcafdf4d377562ec33
    """
    ipfs_content = read_parquet_with_retry(
        "https://cloudflare-ipfs.com/ipfs/QmWpnErRwVRLqdGsBC2J9NMngwzJtWErDZvf6wDqJ1ZVis"
    )
    return ipfs_content


@asset(compute_kind="API", group_name="private_api")
def dune_allo_deployments(
    dune: DuneResource, raw_allo_deployments: pd.DataFrame
) -> None:
    """
    Uploads allo deployments to Dune.
    """
    dune.upload_csv(raw_allo_deployments, "allo_contract_deployments")


@asset(compute_kind="API", group_name="private_api")
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


@retry(tries=8, delay=2, backoff=2, max_delay=10)
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
    url = GIVETH_GQL_ENDPOINT
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
        catalog = read_json_with_retry(f"{forum_address}/categories.json")
        catalog = catalog["category_list"]["categories"]
        for category in catalog:
            category["source"] = community
        data.extend(catalog)

    discourse_df = pd.DataFrame(data)
    discourse_df = discourse_df.convert_dtypes()
    return discourse_df
