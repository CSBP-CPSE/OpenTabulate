# OpenTabulate

OpenTabulate is a Python package designed to organize, tabulate, and process structured data. It currently aims to be a data processing framework for the [Linkable Open Data Environment](https://github.com/CSBP-CPSE/LODE-ECDO), an exploratory project by the Data Exploration and Integration Lab (DEIL) within the Center for Special Business Projects (CSBP) at Statistics Canada. OpenTabulate offers

- automated data retrieval
- a systematic way of organizing and retrieving data using *sources files* (inspired by [OpenAddresses](https://openaddresses.io/)),
- tabulation of data into a standardized CSV format that is suitable for merging and linkage,
- various methods to process data, including address parsing, cleaning and reformatting.

OpenTabulate's API defines several classes and methods, such that when put together form a *processing pipeline*. This simplifies the processing procedure as a sequence of class method invocations. Moreover, this design allows for ease of addition, modification and removal of code.

## Requirements

A basic setup of the data processing software will at least require

- [Python](https://www.python.org/downloads/) (version 3.5+)
- [requests](http://docs.python-requests.org/en/master/), compatible with your verison of Python

## Optional dependencies

To process sources with the `address_str` key, an address parser is required. Below are the currently supported address parsers.

- [libpostal](https://github.com/openvenues/libpostal) (and [pypostal](https://github.com/openvenues/pypostal) for Python bindings)

## Installation

Be sure to have a Python package manager that can access the [Python Package Index](https://pypi.org). For example, if you have `pip`, run

```
$ pip install opentabulate
```

After installing the package, initialize the OpenTabulate environment by running

```
$ opentab --initialize DATA_DIR
```

where `DATA_DIR` is a path to a (preferably empty) directory. This configures OpenTabulate to read, write and organize data in `DATA_DIR`.

## Documentation

~~Please see our documentation [here](https://opentabulate.readthedocs.io/en/latest/).

## Issues

You can post questions, enhancement requests, and bugs in [Issues](https://github.com/CSBP-CPSE/OpenTabulate/issues).
