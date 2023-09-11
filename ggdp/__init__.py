import os

from dagster import Definitions, load_assets_from_modules
from dagster_duckdb_pandas import DuckDBPandasIOManager

from . import assets

DBT_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../dbt/"

all_assets = load_assets_from_modules([assets])

resources = {
    "io_manager": DuckDBPandasIOManager(database="data/dbt.duckdb"),
}

defs = Definitions(assets=all_assets, resources=resources)
