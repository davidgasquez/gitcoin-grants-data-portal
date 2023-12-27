.DEFAULT_GOAL := run

run:
	@dagster asset materialize --select \* -m ggdp

dev:
	@dagster dev -m ggdp

test:
	@cd dbt && dbt test

preview:
	@quarto preview portal

render:
	@quarto render portal

publish:
	@quarto publish gh-pages portal --no-prompt

clean:
	@rm -rf portal/.quarto data/*.parquet data/*.duckdb
	@rm -rf dbt/target dbt/logs dbt/dbt_packages
