# HyperTrade

This is the README for getting started working in the HyperTrade monorepo.

## Prerequisites

- [Git](https://git-scm.com/downloads)
- [Docker](https://www.docker.com/products/docker-desktop)
- [VSCode](https://code.visualstudio.com/download)

## Getting started

### Cloning the repo

To clone the repo, navigate to the directory you want to clone the repo to and run the following command:

```bash
git clone git@github.com:mbecker8600/HyperTrade.git
```

### Open VSCode

Open VSCode to the cloned directory and be sure to open in Container. This project utilizes dev containers so that all depenendencies are managed through docker files for development.

## Packages

- [**`libs/simulator`**](libs/simulator/README.md): Core classes and services for simulating trading strategies.
- [**`libs/data`**](libs/data/README.md): Tools for fetching and managing market data.
- [**`libs/strategy`**](libs/strategy/README.md): Modules for creating and testing trading strategies.
- [**`libs/analysis`**](libs/analysis/README.md): Utilities for analyzing trading strategy performance.
- [**`libs/util`**](libs/util/README.md): Miscellaneous utility functions and classes.

## Using the monorepo

### Running all tests

```bash
bazelisk test ...
```

### Adding a new package (Python)

To add a new package to the monorepo, you can run the following command from the root of the monorepo:

```bash
pip install <package-name>
pip freeze > third-party/requirements.txt
```

## Contributing

If you would like to contribute to the HyperTrade project, please follow the [contributing guidelines](CONTRIBUTING.md).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
