# Running OpenTabulate

## Directory initialization

A command-line tool `tabctl.py` is provided as an interface to the OpenTabulate API. After cloning the OpenTabulate repository, change into the cloned directory and run

```
$ python tools/tabctl.py --initialize
```

where you may substitute `python` for the name of your Python 3 binary. The `--initialize` flag creates a set of directories

```
OpenTabulate/
└──pddir/
   ├── raw/
   ├── pre/
   ├── dirty/
   └── clean/
```

which are data processing directories:

| Directory | Description |
| ---- | ----------- |
| `raw` | Source datasets should be stored here, noting that if your dataset is specified by `url` in a source file, it will be downloaded to this directory. |
| `pre` | Datasets flagged for pre-processing are sent here from `raw`. |
| `dirty` | Datasets from `raw` or `pre` are sent here during processing. They represent datasets converted to CSV format that have not been cleaned yet. |
| `clean` | Datasets are sent here after cleaning. |

## Command-line usage

#### General usage

```
tabctl.py [optional arguments] SOURCE ...
```

#### Postional arguments

`SOURCE` is the path of your [source file](CONTRIB.md) corresponding to the data you want to process. You may list multiple source files to process in the same command. Remember that you must put the data in `raw` if you do not provide a `url` key in the source file!

#### Optional arguments

| Short flag | Long flag | Description |
| ---------- | --------- | ----------- |
| `-h` | `--help` | Print the command-line tool help prompt to standard output. |
| `-p` | `--ignore-proc` | Do not process the datasets corresponding the source file. Useful for quickly checking source file syntax. |
| `-u` | `--ignore-url` | Do not download any data provided in all `url` keys. Useful to save bandwidth. |
| `-z` | `--no-decompress` | Do not decompress data that was downloaded as a compressed archive. Useful if you already decompressed the data. |
| `-j N` | `--jobs N` | Run asynchronous data processing jobs, where at most *N* processes can simultaneously be running. *N* must be a positive integer. |
|  | `--initialize` | Create the data processing directories used by `tabctl.py` and `opentabulate.py`. |
|  | `--pre` | **(EXPERIMENTAL)** Allow execution of pre-processing scripts from `pre` keys. |
|  | `--post` | Allow execution of post-processing scripts from `post` keys. |
|  | `--log FILE` | **(NOT AVAILABLE)** |

#### Summary

A summary of the usage is given by the `argparse` help prompt 

```
usage: tabctl.py [-h] [-b] [-p] [-u] [-z] [--pre] [--post] [-j N] [--log FILE]
                 [--initialize]
                 [SOURCE [SOURCE ...]]

A command-line interactive tool with the OBR.

positional arguments:
  SOURCE               path to source file

optional arguments:
  -h, --help           show this help message and exit
  -p, --ignore-proc    check source files without processing data
  -u, --ignore-url     ignore "url" entries from source files
  -z, --no-decompress  do not decompress files from compressed archives
  --pre                (EXPERIMENTAL) allow preprocessing script to run
  --post               (EXPERIMENTAL) allow postprocessing script to run
  -j N, --jobs N       run at most N jobs asynchronously
  --log FILE           (NOT FUNCTIONAL) log output to FILE
  --initialize         create processing directories
```

To print this in your terminal, simply enter

```
$ python tools/tabctl.py --help
```

#### Example use

For the examples below, we have source files `SOURCE1.json` and `SOURCE2.json` stored in the directory `sources` in the OpenTabulate directory.

Basic use:

```
$ python tools/tabctl.py sources/SOURCE1.json
```

Run `tabctl.py` using two CPU cores without downloading data from URLs:

```
$ python tools/tabctl.py -j 2 -u sources/SOURCE1.json sources/SOURCE2.json
```

Test for correct syntax of source file:

```
$ python tools/tabctl.py --ignore-proc sources/SOURCE1.json
```
