.DEFAULT_GOAL := run

run:
	@dagster job execute -j data_assets_job -m ggdp

apis:
	@dagster job execute -j private_apis_assets_job -m ggdp

tables:
	@python -c 'from ggdp import db; db.export_database_to_parquet("data/local.duckdb", "data/tables");'

dev:
	@dagster dev -m ggdp

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
