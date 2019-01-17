#### Important note / Note importante

(EN) This is an exploratory and experimental open project. The project is currently in development and all the material on this page should be considered as part of work in progress. / (FR) Ce projet ouvert est exploratoire et expérimental. Le projet est en cours de développement et tout le contenu de cette page doit être considéré comme faisant partie des travaux en cours.

# OpenBusinessRepository

The OpenBusinessRepository (OBR) is open-source software designed to centralize, process, and clean data. It is inspired by projects such as OpenAddresses and is tailored to publicly available business data, such as open register and licensing information. 

## Open data contribution / Contribution aux données ouvertes

Currently, the project brings together open licensed data from authoritative sources in Canada such as municipal and provincial governments. The current set of data sources is listed in `sources/business-sources.csv`, including their respective links to both the licenses and datasets. 

Part of the future development of this project is to host the processed and cleaned business data on a server for the public to download. You can contribute to the OBR with data available under an open data license. This can be done by referring us to data we do not have on the list or communicating with us directly if you are part of a group that maintains business data. The best way to add new business data is to write a source file for it (see documentation references below).

## Installation / Installation

A basic setup of the data processing software will at least require

- [Python](https://www.python.org/downloads/) (version 3.5+)
- [requests](http://docs.python-requests.org/en/master/), compatible with your verison of Python

Once those are installed, clone the repository

```bash
$ git clone https://github.com/CSBP-CPSE/OpenBusinessRepository
```

and run the command

```shell
$ python tools/obrpdctl.py --initialize
``` 

in the cloned directory to create the data processing directories.

## Optional dependencies / Dépendances optionnelles

To process sources with the `full_addr` tag, an address parser is required. Below are the currently supported address parsers.

- [libpostal](https://github.com/openvenues/libpostal) (and [pypostal](https://github.com/openvenues/pypostal) for Python bindings)

## Help / Aide

#### Interactive data processing script

To print the help prompt, run 

```shell
$ python tools/obrpdctl.py --help
```

which prints

```
usage: obrpdctl.py [-h] [-p] [-u] [-z] [-j N] [--log FILE] [--initialize]
                   [SOURCE [SOURCE ...]]

A command-line interactive tool with the OBR.

positional arguments:
  SOURCE               path to source file

optional arguments:
  -h, --help           show this help message and exit
  -p, --ignore-proc    check source files without processing data
  -u, --ignore-url     ignore "url" entries from source files
  -z, --no-decompress  do not decompress files from compressed archives
  -j N, --jobs N       run at most N jobs asynchronously
  --log FILE           log output to FILE
  --initialize         create processing directories
```

#### Documentation

All of our documentation currently resides in the `docs` folder. The contents are summarized below.

- `APPENDIX.md` : A summary of key features and a few technical bits. A couple of sections here are revelant to those who want to get to know the code.
- `CONTRIB.md` : A manual to get started with writing source files. For a data contributor, we would appreciate if you can also write a source file for your dataset. For numerous source file examples, see `sources`.
- `FAQ.md` : Frequently asked questions page.

If you want to tinker around with the code, the core parts are in the `tools` directory. You may also generate the API documentation of OBR by running

```shell
$ pydoc tools/obr.py
```

## Issues / Problèmes

You can post questions, enhancement requests, and bugs in [Issues](https://github.com/CSBP-CPSE/OpenBusinessRepository/issues).
