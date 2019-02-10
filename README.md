#### Important note / Note importante

(EN) This is an exploratory and experimental open project. The project is currently in development and all the material on this page should be considered as part of work in progress. / (FR) Ce projet ouvert est exploratoire et expérimental. Le projet est en cours de développement et tout le contenu de cette page doit être considéré comme faisant partie des travaux en cours.

# OpenTabulate

OpenTabulate is open-source software designed to centralize, process, and clean data. It is inspired by projects such as OpenAddresses and is designed to reformat, clean, and tabulate data. 

## Installation / Installation

A basic setup of the data processing software will at least require

- [Python](https://www.python.org/downloads/) (version 3.5+)
- [requests](http://docs.python-requests.org/en/master/), compatible with your verison of Python

Once those are installed, clone the repository

```bash
$ git clone https://github.com/CSBP-CPSE/OpenTabulate
```

and run the command

```shell
$ python tools/tabctl.py --initialize
``` 

in the cloned directory to create the data processing directories.

## Optional dependencies / Dépendances optionnelles

To process sources with the `full_addr` key, an address parser is required. Below are the currently supported address parsers.

- [libpostal](https://github.com/openvenues/libpostal) (and [pypostal](https://github.com/openvenues/pypostal) for Python bindings)

## Help / Aide

Please refer to the user-friendly documentation [here](docs/WELCOME.md).

## Issues / Problèmes

You can post questions, enhancement requests, and bugs in [Issues](https://github.com/CSBP-CPSE/OpenTabulate/issues).
