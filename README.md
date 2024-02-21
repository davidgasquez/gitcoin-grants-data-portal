<p align="center">
<img src="https://user-images.githubusercontent.com/1682202/271937380-10d6e036-5fe4-4ea6-b3b4-8e3001c21289.png" data-canonical-src="https://user-images.githubusercontent.com/1682202/271937380-10d6e036-5fe4-4ea6-b3b4-8e3001c21289.png" width="100" />
</p>

# 🌲 Gitcoin Grants Data Portal

[![CI](https://github.com/davidgasquez/gitcoin-grants-data-portal/actions/workflows/run.yml/badge.svg)](https://github.com/davidgasquez/gitcoin-grants-data-portal/actions/workflows/run.yml)

Open source, serverless, and local-first Data Platform for Gitcoin Grants Data. This data hub improves data access and empower data scientists to conduct research that guides community driven analysis.

![dag](https://github.com/davidgasquez/gitcoin-grants-data-portal/assets/1682202/bca9dcfb-718e-4d73-9576-028f1bfefdde)

## 📂 Gitcoin Grants Data

Data is living as multiple Parquet files at IPFS! You can get them all at the [IPFS CID](https://raw.githubusercontent.com/davidgasquez/gitcoin-grants-data-portal/main/data/IPFS_CID) pointer available in this repository.

The following command will give you a working URL to explore the available tables.

```bash
# Get the latest IPFS CID
LATEST_IPFS_CID=$(curl https://raw.githubusercontent.com/davidgasquez/gitcoin-grants-data-portal/main/data/IPFS_CID)

# Print the Gateway URL with all the tables
echo https://ipfs.filebase.io/ipfs/$LATEST_IPFS_CID/data/
```

### 📌 IPNS

You can also go to [`https://k51qzi5uqu5dhn3p5xdkp8n6azd4l1mma5zujinkeewhvuh5oq4qvt7etk9tvc.ipns.dweb.link/data/`](https://k51qzi5uqu5dhn3p5xdkp8n6azd4l1mma5zujinkeewhvuh5oq4qvt7etk9tvc.ipns.dweb.link/data/), which points to the latest available data via IPNS.

You can use IPNS from your favorite tools. E.g: `pd.read_parquet('https://ipfs.filebase.io/ipns/k51qzi5uqu5dhn3p5xdkp8n6azd4l1mma5zujinkeewhvuh5oq4qvt7etk9tvc/data/allo_rounds.parquet')`

## 📖 Overview

The repository contains code and artifacts to help process Gitcoin Grants data from the [Grants Stack Indexer API](https://github.com/gitcoinco/grants-stack-indexer). It is an instance of [Datadex](https://github.com/davidgasquez/datadex) allowing you and everyone else to:

- Add new data sources to the portal, collaborate on better models (ala Dune) or submit an interesting analysis.
- All in a permissionless way. Don't ask, fork it and improve the models, add a new source or update any script.
- Declarative stateless transformations tracked in git, executed in GitHub Actions and published to IPFS. Data, artifacts (like the entire DuckDB database), and models all version controlled.
- Share and explore dashboards and report with the world!

> [!TIP]
> You can read more on the [motivation and the approach on my blog](https://davidgasquez.github.io/gitcoin-data/)!

## ⚙️ Quick Start

The fastest way to start working on the Data Portal is via [VSCode Remote Containers](https://code.visualstudio.com/docs/remote/containers). Once inside the develpment environment, you can run `make dev` to spin up the Dagster UI.

The development environment can also run in your browser thanks to GitHub Codespaces! Just click on the badge below to get started.

[![badge](https://github.com/codespaces/badge.svg)](https://codespaces.new/davidgasquez/gitcoin-grants-data-portal)

### 🛠️ Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. There are multiple interesting ways to contribute to this project:

- Add [new data sources](ggdp/assets.py)
- Improve [dbt project](dbt/) models
- Write a one off [report](reports/)

### 📄 License

[MIT](https://choosealicense.com/licenses/mit/).
