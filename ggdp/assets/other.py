import pandas as pd
import requests
from dagster import Backoff, RetryPolicy, asset
from tenacity import retry, wait_exponential, stop_after_attempt

from ..resources import DuneResource


@asset(
    retry_policy=RetryPolicy(max_retries=3, delay=0.2, backoff=Backoff.EXPONENTIAL),
)
def raw_chain_metadata() -> pd.DataFrame:
    """
    Metadata for chains on which Gitcoin indexer registered at least one round. Source: `chainid.network/chains.json`
    """

    df = pd.read_json("https://chainid.network/chains.json")
    df = df.convert_dtypes()
    df["chainId"] = df["chainId"].astype(str)

    return df


@asset(compute_kind="API")
def dune_allo_deployments(
    dune: DuneResource, raw_allo_deployments: pd.DataFrame
) -> None:
    """
    Uploads allo deployments to Dune.
    """
    dune.upload_csv(raw_allo_deployments, "allo_contract_deployments")


# @asset(compute_kind="API")
# def ethereum_project_registry_tx(covalent_api: CovalentAPIResource):
#     """
#     All Ethereum mainnet transactions targeting project registry, from Covalent
#     """

#     all_tx = covalent_api.fetch_all_tx_for_address(
#         "eth-mainnet", "0x03506eD3f57892C85DB20C36846e9c808aFe9ef4"
#     )

#     dataframes = [pd.DataFrame(data.get("items")) for data in all_tx]
#     combined_df = pd.concat(dataframes, ignore_index=True)

#     return combined_df


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


@retry(
    stop=stop_after_attempt(8),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
def get_hypercerts(gql_endpoint, creator_addresses):
    query = """
    query ClaimsQuery($creatorAddresses: [String]!) {
      claims(first: 1000, where: {creator_in: $creatorAddresses}) {
        id
        creation
        tokenID
        contract
        uri
        totalUnits
        creator
      }
    }
    """
    payload = {"query": query, "variables": {"creatorAddresses": creator_addresses}}

    response = requests.post(gql_endpoint, json=payload)
    response.raise_for_status()
    return response.json()["data"]["claims"]


@asset
def raw_hypercert_claims(raw_allo_projects) -> pd.DataFrame:
    """
    Listing of hypercerts created by Allo Grantees

    Source: https://thegraph.com/hosted-service/subgraph/hypercerts-admin/hypercerts-optimism-mainnet
    """
    HYPERCERTS_ENDPOINT = "https://api.thegraph.com/subgraphs/name/hypercerts-admin/hypercerts-optimism-mainnet"
    grantees = list(raw_allo_projects.createdByAddress.str.lower().unique())

    all_certs = []

    window_size = 1000
    for start_index in range(0, len(grantees), window_size):
        window_creators = grantees[start_index : start_index + window_size]
        result = get_hypercerts(HYPERCERTS_ENDPOINT, window_creators)
        all_certs.extend(result)

    certs_df = pd.DataFrame(all_certs)
    certs_df.uri = certs_df.uri.str.replace("ipfs://", "")

    certs_df = certs_df.convert_dtypes()

    return certs_df


@retry(
    stop=stop_after_attempt(8),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
def get_attestations(endpoint, schema):
    query = """
    query ($schemaId: SchemaWhereUniqueInput!) {
        schema(where: $schemaId) {
            attestations(take:5000) {
                attester
                recipient
                isOffchain
                timeCreated
                decodedDataJson
            }
        }
    }
    """
    payload = {
        "query": query,
        "variables": {"schemaId": {"id": schema}},
    }

    response = requests.post(endpoint, json=payload)
    response.raise_for_status()

    return response.json()["data"]["schema"]["attestations"]


@asset(compute_kind="EAS")
def raw_karmahq_attestations():
    """
    Attestations made by KarmaHQ on Optimism. Some attesters are also Gitcoin grantees.

    Source: EAS GraphQL api
    """
    EAS_OP_ENDPOINT = "https://optimism.easscan.org/graphql"
    EAS_OP_DETAILS_SCHEMA = (
        "0x70a3f615f738fc6a4f56100692ada93d947c028b840940d97af7e7d6f0fa0577"
    )
    # List of schemas, most attestations don't carry data hance need for `DETAILS`
    # https://github.com/show-karma/karma-gap-sdk/blob/4789422f1627fa7b575cc66cd0bf20c59ca1038a/core/consts.ts#L45

    from_eas = pd.DataFrame(
        get_attestations(EAS_OP_ENDPOINT, schema=EAS_OP_DETAILS_SCHEMA)
    )
    from_eas = from_eas.convert_dtypes()
    return from_eas
