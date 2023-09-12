# 🌲 Gitcoin Grants Data Portal

Open source, serverless, and local-first data hub for Gitcoin Grants data!

The repository contains code and artifacts to help process Gitcoin Grants data from the [Allo Indexer Data API](https://indexer-grants-stack.gitcoin.co/data/). It is an instance of [Datadex](https://github.com/davidgasquez/datadex) allowing you and everyone else to:

- Add new data sources to the portal, collaborate on better models (ala Dune) or submit an interesting analysis.
- All in a permissionless way. Don't ask, fork it and improve the models, add a new source or update any script.
- Declarative stateless transformations tracked in git, executed in GitHub Actions and published to IPFS. Data, artifacts (like the entire DuckDB database), and models all version controlled.
- Share and explore dashboards and report with the world!

## ⚙️ Setup

The fastest way to start using Datadex is via [VSCode Remote Containers](https://code.visualstudio.com/docs/remote/containers). Once inside the develpment environment, you'll only need to run `make deps`.

[![](https://github.com/codespaces/badge.svg)](https://codespaces.new/davidgasquez/datadex)

PS: The development environment can also run in your browser thanks to GitHub Codespaces!
