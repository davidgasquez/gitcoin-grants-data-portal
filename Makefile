.DEFAULT_GOAL := run

run:
	@dagster asset materialize --select \* -m ggdp;

dev:
	@dagster dev -m ggdp;

preview:
	@quarto preview

publish:
	@quarto publish gh-pages --no-prompt

clean:
	@dbt clean --project-dir dbt;
	@rm -rf output .quarto logs
	@rm data/*.parquet data/*.duckdb
