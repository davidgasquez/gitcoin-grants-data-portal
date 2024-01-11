import os

from dagster import Definitions, load_assets_from_modules, EnvVar
from dagster_dbt import dbt_cli_resource, load_assets_from_dbt_project
from dagster_duckdb import DuckDBResource
from dagster_duckdb_pandas import DuckDBPandasIOManager

from . import assets
from . import resources as res

DBT_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../dbt/"

dbt_resource = dbt_cli_resource.configured(
    {"project_dir": DBT_PROJECT_DIR, "profiles_dir": DBT_PROJECT_DIR}
)

dbt_assets = load_assets_from_dbt_project(DBT_PROJECT_DIR, DBT_PROJECT_DIR)
all_assets = load_assets_from_modules([assets])

resources = {
    "covalentAPI": res.CovalentAPIResource(API_KEY=EnvVar("COVALENT_API_KEY")),
    "dbt": dbt_resource,
    "duckdb": DuckDBResource(database="data/local.duckdb"),
    "io_manager": DuckDBPandasIOManager(
        database="data/local.duckdb",
    ),
}

defs = Definitions(assets=[*dbt_assets, *all_assets], resources=resources)
