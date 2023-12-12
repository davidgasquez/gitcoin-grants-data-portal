.DEFAULT_GOAL := run

run:
	@dagster asset materialize --select \* -m ggdp

dev:
	@dagster dev -m ggdp

preview:
	@quarto preview

render:
	@quarto render

publish:
	@quarto publish gh-pages --no-prompt

clean:
	@rm -rf portal/.quarto data/*.parquet data/*.duckdb
	@rm -rf dbt/target dbt/logs dbt/dbt_packages
