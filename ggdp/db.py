import os

import duckdb
import pandas as pd

DATA_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../data"


def query(sql) -> pd.DataFrame:
    """Query the local DuckDB and return a pandas dataframe

    Args:
        sql (str): SQL query

    Returns:
        pandas.DataFrame: Query result
    """
    with duckdb.connect(database=f"{DATA_DIR}/local.duckdb", read_only=True) as con:
        return con.sql(sql).df()


def export_database_to_parquet(db_path: str, output_path: str) -> None:
    """Export the local DuckDB database to a parquet file

    Args:
        str (path): Path to the parquet file
    """
    with duckdb.connect(database=db_path, read_only=True) as con:
        con.execute(
            f"EXPORT DATABASE '{output_path}' (FORMAT PARQUET, COMPRESSION ZSTD, ROW_GROUP_SIZE 100000);"
        )
