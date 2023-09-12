FROM mcr.microsoft.com/devcontainers/python:3

# Install Quarto
RUN curl -sL $(curl https://quarto.org/docs/download/_download.json | grep -oP "(?<=\"download_url\":\s\")https.*${ARCH}\.deb") --output /tmp/quarto.deb \
    && dpkg -i /tmp/quarto.deb \
    && rm /tmp/quarto.deb

# Setup environment
ENV PROJECT_DIR /workspaces/gitcoin-grants-data-portal
ENV DATA_DIR "${PROJECT_DIR}/data"
ENV DBT_PROFILES_DIR "${PROJECT_DIR}/dbt"
ENV DATABASE_URL "duckdb:///${DATA_DIR}/dbt.duckdb"

# Install Python Dependencie
WORKDIR /workspaces/gitcoin-grants-data-portal
COPY . .
RUN pip install -e ".[dev]"
