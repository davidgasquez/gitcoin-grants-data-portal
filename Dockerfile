FROM mcr.microsoft.com/devcontainers/python:3.11

# Install Quarto
RUN curl -sL $(curl https://quarto.org/docs/download/_download.json | grep -oP "(?<=\"download_url\":\s\")https.*${ARCH}\.deb") --output /tmp/quarto.deb \
    && dpkg -i /tmp/quarto.deb \
    && rm /tmp/quarto.deb

# Working Directory
ENV WORKDIR "/workspaces/gitcoin-grants-data-portal"
WORKDIR ${WORKDIR}

# Environment Variables
ENV PROJECT_DIR "${WORKDIR}"
ENV DATA_DIR "${WORKDIR}/data"
ENV DBT_PROFILES_DIR "${WORKDIR}/dbt"
ENV DATABASE_URL "duckdb:///${DATA_DIR}/dbt.duckdb"
ENV DAGSTER_HOME "/home/vscode"

# Install Python Dependencie
COPY . .
RUN pip install -e ".[dev]"
