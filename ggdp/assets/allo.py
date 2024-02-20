import json

import pandas as pd
from dagster import Backoff, RetryPolicy, asset
from regex import R

from ..resources import GrantsStackIndexerGraphQL


@asset
def raw_allo_applications(indexer_graphql: GrantsStackIndexerGraphQL) -> pd.DataFrame:
    query = """
    {
        applications {
            anchorAddress
            chainId
            createdAtBlock
            createdByAddress
            id
            metadata
            metadataCid
            nodeId
            projectId
            roundId
            status
            statusSnapshots
            statusUpdatedAtBlock
            tags
            totalAmountDonatedInUsd
            totalDonationsCount
            uniqueDonorsCount
        }
    }
    """
    response = indexer_graphql.query(query)
    df = pd.DataFrame(response["data"]["applications"]).convert_dtypes()
    df["metadata"] = df["metadata"].apply(lambda x: json.dumps(x))

    return df


@asset
def raw_allo_rounds(indexer_graphql: GrantsStackIndexerGraphQL) -> pd.DataFrame:
    query = """
    {
        rounds {
            adminRole
            applicationMetadata
            applicationMetadataCid
            applicationsEndTime
            applicationsStartTime
            chainId
            createdAtBlock
            createdByAddress
            donationsEndTime
            donationsStartTime
            id
            isReadyForPayout
            managerRole
            matchAmount
            matchAmountInUsd
            matchTokenAddress
            nodeId
            projectId
            roundMetadata
            roundMetadataCid
            strategyAddress
            strategyId
            strategyName
            tags
            totalAmountDonatedInUsd
            totalDonationsCount
            uniqueDonorsCount
            updatedAtBlock
        }
    }
    """
    response = indexer_graphql.query(query)
    df = pd.DataFrame(response["data"]["rounds"])

    df["roundMetadata"] = df["roundMetadata"].apply(lambda x: json.dumps(x))
    df["applicationMetadata"] = df["applicationMetadata"].apply(lambda x: json.dumps(x))
    df["tags"] = df["tags"].apply(lambda x: json.dumps(x))

    df = df.convert_dtypes()
    return df


@asset
def raw_allo_donations(indexer_graphql: GrantsStackIndexerGraphQL) -> pd.DataFrame:
    query = """
        query($first: Int, $offset: Int) {
            donations(first: $first, offset: $offset) {
                amountInUsd
                amount
                amountInRoundMatchToken
                applicationId
                blockNumber
                chainId
                id
                donorAddress
                nodeId
                projectId
                recipientAddress
                roundId
                tokenAddress
                transactionHash
            }
        }
        """
    response = indexer_graphql.paginated_query(query, size=50000)
    df = pd.DataFrame(response).convert_dtypes()

    return df


@asset
def raw_allo_prices(indexer_graphql: GrantsStackIndexerGraphQL) -> pd.DataFrame:
    query = """
    {
        prices {
            blockNumber
            chainId
            id
            nodeId
            priceInUsd
            timestamp
            tokenAddress
        }
    }
    """
    response = indexer_graphql.query(query)
    return pd.DataFrame(response["data"]["prices"])


@asset
def raw_allo_projects(indexer_graphql: GrantsStackIndexerGraphQL) -> pd.DataFrame:
    query = """
    {
        projects {
            anchorAddress
            chainId
            createdAtBlock
            createdByAddress
            id
            metadata
            metadataCid
            name
            nodeId
            nonce
            projectNumber
            projectType
            registryAddress
            tags
            updatedAtBlock
        }
    }
    """
    response = indexer_graphql.query(query)
    df = pd.DataFrame(response["data"]["projects"])
    df["metadata"] = df["metadata"].apply(lambda x: json.dumps(x))
    df = df.convert_dtypes()

    return df


@asset
def raw_allo_round_roles(indexer_graphql: GrantsStackIndexerGraphQL) -> pd.DataFrame:
    query = """
    {
        roundRoles {
            address
            chainId
            createdAtBlock
            nodeId
            role
            roundId
        }
    }
    """
    response = indexer_graphql.query(query)
    return pd.DataFrame(response["data"]["roundRoles"])


@asset
def raw_allo_subscriptions(indexer_graphql: GrantsStackIndexerGraphQL) -> pd.DataFrame:
    query = """
    {
        subscriptions {
            chainId
            contractAddress
            contractName
            createdAt
            fromBlock
            id
            indexedToBlock
            indexedToLogIndex
            nodeId
            toBlock
            updatedAt
        }
    }
    """
    response = indexer_graphql.query(query)
    return pd.DataFrame(response["data"]["subscriptions"])


@asset(retry_policy=RetryPolicy(max_retries=3, delay=0.2, backoff=Backoff.EXPONENTIAL))
def raw_allo_deployments() -> pd.DataFrame:
    """
    Deployment address for all official allo contract deployments by Allo team, collected 07.01.24

    Canonical source: https://github.com/allo-protocol/allo-contracts/blob/main/docs/CHAINS.md
    Ingestion logic: https://gist.github.com/DistributedDoge/57e39c3e5cc207fcafdf4d377562ec33
    """
    ipfs_content = pd.read_parquet(
        "https://ipfs.io/ipfs/QmWpnErRwVRLqdGsBC2J9NMngwzJtWErDZvf6wDqJ1ZVis"
    )
    return ipfs_content
