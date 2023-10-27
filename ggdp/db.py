import os

import duckdb
import pandas as pd

DATA_DIR = os.getenv("DATA_DIR", "../data")


def query(sql) -> pd.DataFrame:
    """Query the local DuckDB and return a pandas dataframe

    Args:
        sql (str): SQL query

    Returns:
        pandas.DataFrame: Query result
    """
    with duckdb.connect(database=f"{DATA_DIR}/dbt.duckdb", read_only=True) as con:
        return con.sql(sql).df()
