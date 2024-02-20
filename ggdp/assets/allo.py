import json

import pandas as pd
from dagster import asset

from ..resources import GrantsStackIndexerGraphQL


@asset
def allo_applications(indexer_graphql: GrantsStackIndexerGraphQL) -> pd.DataFrame:
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
    return pd.DataFrame(response["data"]["applications"])


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

    df.convert_dtypes()
    return df


@asset
def allo_donations(indexer_graphql: GrantsStackIndexerGraphQL) -> pd.DataFrame:
    query = """
    {
        donations {
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
    response = indexer_graphql.query(query)
    return pd.DataFrame(response["data"]["donations"])
