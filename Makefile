.DEFAULT_GOAL := run

run:
	@dagster asset materialize --select \* -m ggdp

tables:
	@python -c 'from ggdp import db; db.export_database_to_parquet("data/local.duckdb", "data/tables");'

dev:
	@dagster dev

setup:
	@command -v uv >/dev/null 2>&1 || pip install -U uv
	uv venv
	uv pip install -U -e .[dev]
	. .venv/bin/activate

test:
	@cd dbt && dbt test

preview:
	@quarto preview portal

render:
	@cd dbt && dbt docs generate
	@mkdir -p dbt/target/docs
	@cp dbt/target/*.json dbt/target/index.html dbt/target/graph.gpickle dbt/target/docs/
	@quarto render portal
	@cp -r dbt/target/docs/ portal/_site/dbt

publish:
	@quarto publish gh-pages portal --no-prompt

clean:
	@rm -rf portal/.quarto data/*.parquet data/*.duckdb portal/_site
	@rm -rf dbt/target dbt/logs dbt/dbt_packages
