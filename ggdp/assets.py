import pandas as pd
from dagster import asset
from fsspec.implementations.http import HTTPFileSystem

ALLO_INDEXER_URL = "https://indexer-grants-stack.gitcoin.co/data"


def chain_file_aggregator(json_name):
    fs = HTTPFileSystem(simple_links=True)
    paths = fs.ls(ALLO_INDEXER_URL)
    paths = [path["name"] for path in paths if path["name"].split("/")[-1].isdigit()]
    df = pd.DataFrame()
    for path in paths:
        chain_id = int(path.split("/")[-1])
        df_chain = pd.read_json(f"{path}/{json_name}")
        df_chain["chainId"] = chain_id
        df = pd.concat([df, df_chain])
    return df


@asset
def raw_passport_scores() -> pd.DataFrame:
    file_url = f"{ALLO_INDEXER_URL}/passport_scores.json"
    df = pd.read_json(file_url)
    df = df.drop(columns=["error"])
    df["last_score_timestamp"] = pd.to_datetime(
        df["last_score_timestamp"], errors="coerce"
    )
    return df[df["address"].str.startswith("0x")]


@asset
def raw_projects() -> pd.DataFrame:
    return chain_file_aggregator("projects.json")


@asset
def raw_prices() -> pd.DataFrame:
    return chain_file_aggregator("prices.json")


@asset
def raw_rounds() -> pd.DataFrame:
    return chain_file_aggregator("rounds.json")
