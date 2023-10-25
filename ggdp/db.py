import os

import duckdb

DATA_DIR = os.getenv("DATA_DIR", "../data")
con = duckdb.connect(database=f"{DATA_DIR}/dbt.duckdb", read_only=True)


def query(sql):
    return con.sql(sql)
