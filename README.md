# OpenTabulate

OpenTabulate is a Python package designed to organize, tabulate, and process structured data. It currently aims to be a data processing framework for the [Linkable Open Data Environment](https://github.com/CSBP-CPSE/LODE-ECDO), an exploratory project by the Data Exploration and Integration Lab (DEIL) within the Center for Special Business Projects (CSBP) at Statistics Canada. OpenTabulate offers

- a systematic way of organizing data using *sources files* (inspired by [OpenAddresses](https://openaddresses.io/)),
- tabulation of data into a common format (CSV) and common schema that is suitable for merging and linkage,
- basic data cleaning and formatting, data filtering and customizing output schema.

## Requirements

This package is meant to be run on a Linux-based distribution. Using the package only requires

- [Python](https://www.python.org/downloads/) (version 3.5+)

## Installation

Install the `opentabulate` package from the [Python Package Index](https://pypi.org) using whatever Python package manager you choose. For example, with `pip` installed you may simply run

```
$ pip3 install opentabulate
```

with any Python environment.

After installing the package, copy the OpenTabulate configuration file using the built-in command line flag.

```
$ opentab --copy-config
```

This copies the file `opentabulate.conf.example` from the package installation to `$HOME/.config/opentabulate.conf`. Provide a directory for the `root_directory` variable in the configuration, which will specify where the datasets will be loaded from and tabulated to. Configure the remaining variables as needed. Next run

```
opentab --initialize
```

which creates the subdirectories in `root_directory`. Now OpenTabulate is ready to run.

## Documentation

For more information, please read our documentation [here](https://opentabulate.readthedocs.io/en/stable/).

## Issues

You can post questions, enhancement requests, and bugs in [Issues](https://github.com/CSBP-CPSE/OpenTabulate/issues).
