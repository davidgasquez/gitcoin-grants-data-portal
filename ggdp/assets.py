import pandas as pd
from dagster import asset
from fsspec.implementations.http import HTTPFileSystem

ALLO_INDEXER_URL = "https://indexer-production.fly.dev/data"


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
                df_round = pd.read_json(f"{round}/{json_name}")
            except Exception as e:
                print(f"Error reading {round}/{json_name}")
                print(f"Error: {e}")
                continue
            df_round["chainId"] = str(chain_id)
            df_round["roundId"] = str(round_id)
            df = pd.concat([df, df_round])
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
    return chain_file_aggregator("projects.json")


@asset
def raw_prices() -> pd.DataFrame:
    return chain_file_aggregator("prices.json")


@asset
def raw_rounds() -> pd.DataFrame:
    return chain_file_aggregator("rounds.json")


@asset
def raw_round_votes() -> pd.DataFrame:
    return round_file_aggregator("votes.json")


@asset
def raw_round_applications() -> pd.DataFrame:
    return round_file_aggregator("applications.json")


@asset
def raw_round_contributors() -> pd.DataFrame:
    return round_file_aggregator("contributors.json")
