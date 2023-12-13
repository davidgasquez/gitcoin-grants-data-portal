FROM mcr.microsoft.com/devcontainers/python:3.11

# Install Quarto
RUN curl -sL $(curl https://quarto.org/docs/download/_prerelease.json | grep -oP "(?<=\"download_url\":\s\")https.*${ARCH}\.deb") --output /tmp/quarto.deb \
    && dpkg -i /tmp/quarto.deb \
    && rm /tmp/quarto.deb

# Environment Variables
ENV DAGSTER_HOME "/home/vscode"
ENV WORKSPACE "/workspaces/gitcoin-grants-data-portal"

# Working Directory
WORKDIR ${WORKSPACE}
