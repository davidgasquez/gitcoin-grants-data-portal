import os

from dagster import EnvVar, Definitions, load_assets_from_modules
from dagster_dbt import DbtCliResource, load_assets_from_dbt_project
from dagster_duckdb import DuckDBResource
from dagster_duckdb_pandas import DuckDBPandasIOManager

from . import resources as res
from .assets import allo, other

DBT_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../dbt/"

dbt_resource = DbtCliResource(project_dir=DBT_PROJECT_DIR, profiles_dir=DBT_PROJECT_DIR)

dbt_assets = load_assets_from_dbt_project(DBT_PROJECT_DIR, DBT_PROJECT_DIR)
python_assets = load_assets_from_modules([allo, other])

resources = {
    "covalent_api": res.CovalentAPIResource(API_KEY=EnvVar("COVALENT_API_KEY")),
    "dune": res.DuneResource(DUNE_API_KEY=EnvVar("DUNE_API_KEY")),
    "indexer_graphql": res.GrantsStackIndexerGraphQL(),
    "dbt": dbt_resource,
    "duckdb": DuckDBResource(database="data/local.duckdb"),
    "io_manager": DuckDBPandasIOManager(database="data/local.duckdb"),
}

defs = Definitions(
    assets=[*dbt_assets, *python_assets],
    resources=resources,
)
