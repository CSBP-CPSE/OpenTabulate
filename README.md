# OpenBusinessRepository
The OpenBusinessRepository (OBR) is a listing of businesses records from open data sources. It includes only data or information that is  available to the public on the Internet under an open data license.

The management and progression of the project is openly available as well at [taiga.io - OpenBusinessRepository](https://tree.taiga.io/project/virtualtorus-openbusinessrepository/).

## Open data contribution

Our repository already contains a source file section and `sources.csv` for open data that we have obtained and points of reference to that data. In the future we plan to host the processed and cleaned data on a server for the public to download.

We are open to people contributing business data under the open data license. This can vary from referring us to data we do not have on the list or communicating with us directly if you are a group that maintains business data. We do not have a rigid process in doing this, but it would be appreciated that if you do refer us to data, that you write a source file for it (see documentation references below).

## Installation

The host of the production system must be a Linux-based operating system, so packages such as `coreutils` are (often) included by default. Simply clone the repository:

```bash
$ git clone https://github.com/CSBP-CPSE/OpenBusinessRepository
```
Then execute the `obr-init.py` script to create the data processing directories.

To operate the data processing, which is managed by the `pdctl.py` script, you will need to install:
- Python (version 3.5+)
- [libpostal](https://github.com/openvenues/libpostal)
- [pypostal](https://github.com/openvenues/pypostal)

## Help

#### Interactive script and code

Assuming you are in the cloned directory, run 

```shell
$ python tools/pdctl.py --help
```

which should print to standard output:

```
usage: pdctl.py [-h] [-p] [-u] [-j N] [--log FILE] SOURCE [SOURCE ...]

A command-line interactive tool with the OBR.

positional arguments:
  SOURCE             path to source file

optional arguments:
  -h, --help         show this help message and exit
  -p, --ignore-proc  check source files without processing data
  -u, --ignore-url   ignore "url" entries from source files
  -j N, --jobs N     run at most N jobs asynchronously
  --log FILE         log output to FILE
```

#### Documentation

In the `docs` folder there is documentation set up to teach you how to write source files, a primer to operate the system, and so forth.

- `CONTRIB.md` : A manual describing the features and options when writing a source file. For source file examples, see `sources`.
- `SCHEME.md` : A summary of the production system and its features.
- `FAQ.md` : Frequently asked questions page.
- `SCRIPTS.md` : N/A.

If you are interested in developing or inspecting the code, it has been commented and documented to the best of our ability.

## Issues

Post questions, enhancement requests, and bugs in [Issues](https://github.com/CSBP-CPSE/OpenBusinessRepository/issues).

## Additional remarks

For code readability and ease of future implementation, most of our code is being ported to `obr.py`. It represents a reimplementation of our production system into the object-oriented programming style. Currently it remains in the `testing` folder and is incomplete with missing documentation.
