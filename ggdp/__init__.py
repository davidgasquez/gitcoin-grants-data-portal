import os

from dagster import Definitions, load_assets_from_modules, define_asset_job
from dagster_dbt import dbt_cli_resource, load_assets_from_dbt_project
from dagster_duckdb import DuckDBResource
from dagster_duckdb_pandas import DuckDBPandasIOManager

from . import assets
from . import ops

DBT_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../dbt/"

dbt_resource = dbt_cli_resource.configured(
    {"project_dir": DBT_PROJECT_DIR, "profiles_dir": DBT_PROJECT_DIR}
)

dbt_assets = load_assets_from_dbt_project(DBT_PROJECT_DIR, DBT_PROJECT_DIR)
all_assets = load_assets_from_modules([assets])

resources = {
    "dbt": dbt_resource,
    "duckdb": DuckDBResource(database="data/local.duckdb"),
    "io_manager": DuckDBPandasIOManager(
        database="data/local.duckdb",
    ),
}

build_all_assets = define_asset_job(
    name="build_all", selection="*", description="Materialize all assets"
)
build_indexer_assets = define_asset_job(
    name="build_light_assets",
    selection=["++rounds", "++projects"],
    description="Materialize downstream of Gitcoin indexer-provided rounds, projects",
)

job_definitions = [ops.refresh_dune, build_all_assets, build_indexer_assets]

defs = Definitions(
    assets=[*dbt_assets, *all_assets], resources=resources, jobs=job_definitions
)
