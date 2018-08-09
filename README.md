# OpenBusinessRepository
The OpenBusinessRepository (OBR) is a production system designed to create a listing of businesses records from open data sources. It includes only data or information that was already available to the public on the Internet, as defined by the open data license.

The management and progression of the project is openly available as well at [taiga.io - OpenBusinessRepository](https://tree.taiga.io/project/virtualtorus-openbusinessrepository/).

## Installation

The host of the production system must be a Linux-based operating system, so packages such as `coreutils` are (often) included by default. Simply clone the repository:
```bash
git clone https://github.com/CSBP-CPSE/OpenBusinessRepository
```
To operate the data processing, which is managed by the `pdctl.py` script, you will need Python 3 and [pypostal](https://github.com/openvenues/pypostal).

## Usage

Assuming you are in the cloned directory, run `python pdctl.py --help` to see available options for the interactive processing script. Please see `./docs/` for documentation on how to get the production system up and running.

## Issues

Post questions, enhancement requests, and bugs in [Issues](https://github.com/CSBP-CPSE/OpenBusinessRepository/issues).
