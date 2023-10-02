<p align="center">
<img src="https://user-images.githubusercontent.com/1682202/271937380-10d6e036-5fe4-4ea6-b3b4-8e3001c21289.png" data-canonical-src="https://user-images.githubusercontent.com/1682202/271937380-10d6e036-5fe4-4ea6-b3b4-8e3001c21289.png" width="100" />
</p>

# 🌲 Gitcoin Grants Data Portal

[![CI](https://github.com/davidgasquez/gitcoin-grants-data-portal/actions/workflows/ci.yml/badge.svg)](https://github.com/davidgasquez/gitcoin-grants-data-portal/actions/workflows/ci.yml)

Proof of Concept for a fully open source, serverless, and local-first data hub for Gitcoin Grants data

![img](https://user-images.githubusercontent.com/1682202/268236925-d44915ab-d46b-49ff-85ec-2ad06bcfe5e0.png)

> You can [find the accompanying post on my blog](https://davidgasquez.github.io/gitcoin-data/)!



## 📖 Overview

The repository contains code and artifacts to help process Gitcoin Grants data from the [Allo Indexer Data API](https://indexer-grants-stack.gitcoin.co/data/). It is an instance of [Datadex](https://github.com/davidgasquez/datadex) allowing you and everyone else to:

- Add new data sources to the portal, collaborate on better models (ala Dune) or submit an interesting analysis.
- All in a permissionless way. Don't ask, fork it and improve the models, add a new source or update any script.
- Declarative stateless transformations tracked in git, executed in GitHub Actions an
d published to IPFS. Data, artifacts (like the entire DuckDB database), and models all version controlled.
- Share and explore dashboards and report with the world!

### 📦 Key Features

- **Open**.
  - Both code and data are fully open source.
  - Also relies on open standards/formats (Arrow ecosystem).
- **Permissionless**.
  - Clone and edit things away! You're not blocked by any API rate limits, or closed data like in Dune.
  - All other git features like branching, merging, pull requests, ... are available because all the data is transformed declaratively as code.
- **Decentralized**.
  - The project runs on a laptop, a server, a CI runner (that's the way is working right now) or a even decentralized compute network like [Bacalhau](https://www.bacalhau.org/). Oh, it even works in GitHub Codespaces so you don't even need to setup anything locally!
  - Data is stored in IPFS. You can run it locally, and it'll generate the same IPFS files if nothing has changed. The more people runst it, the more distributed the IPFS files will be!
  - Data comes from multiple sources and can be exposed in multiple ways.
- **Data as Code**.
  - Every commit generates all the table files and pushes them to IPFS. This means that we can always go back in time and see the data as it was at that point in time. For every commit, we'll have the data as it was at that point in time.
- **Modular**.
  - Each component can be replaced, extended, or removed. Works well in many environments (your laptop, in a cluster, or from the browser), and with multiple tools (tables are files at the end of the day).
- **Low Friction**.
  - Data (raw and processed) is already there! No need to write your own scripts. You can always reproduce it but getting started is as easy as pasting [a SQL query in your browser](https://shell.duckdb.org/) or doing `pd.read_parquet(url)` in a Notebook.
  - Every commit will also publish a set of Quarto Notebooks with the data. Could be used to generate reports/dahsboards, or as documentation.
- **Modern**
  - It supports all the cool things data engineers want; typing, tests, materialized views, dev branches, ...
  - Uses best practices (declarative transformations) and state of the art tooling (DuckDB).

That's it! As an example, you can go to [the generated website with some query examples](https://bafybeieaztvldk23xghlpmzjz5ppry5jrd6bi2kag6q73huckhfrlrabby.ipfs.dweb.link/) or run the following query (rounds by most votes) in [shell.duckdb.org](https://shell.duckdb.org/).

```sql
select
    round_id,
    count(id)
from read_parquet('https://bafybeieaztvldk23xghlpmzjz5ppry5jrd6bi2kag6q73huckhfrlrabby.ipfs.w3s.link/round_votes.parquet')
group by 1 order by 2 desc limit 10;
```

![DuckDB Example](https://user-images.githubusercontent.com/1682202/267361009-a416610e-3905-4399-adac-5d395975c2e5.png)

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
