# Running OpenTabulate

## Directory initialization

The command-line tool `opentab` is shipped with OpenTabulate after installation with `pip`. It is our own tool used to manage the data processing framework that OpenTabulate defines. If you have not done so already, run

```
$ opentab --initialize
```

The `--initialize` flag creates a set of directories

```
~/.opentabulate/
└- pddir/
   └- raw/
   └- pre/
   └- dirty/
   └- clean/
└- sources/
└- scripts/
```

The directories under `pddir` are data processing directories, each described in the table below. Additionally, although the `sources` and `scripts` are not necessary, they are added as a default place to organize your source and script files.

| Directory | Description |
| ---- | ----------- |
| `raw` | Source datasets should be stored here, noting that if your dataset is specified by `url` in a source file, it will be downloaded to this directory. |
| `pre` | Datasets flagged for pre-processing are sent here from `raw`. |
| `dirty` | Datasets from `raw` or `pre` are sent here during processing. They represent datasets converted to CSV format that have not been cleaned yet. |
| `clean` | Datasets are sent here after cleaning. |

## Command-line usage

For general usage, the form is

```
opentab [optional arguments] [SOURCE [SOURCE ...]]
```

`SOURCE` is the path of your [source file](docs/source_files.md) corresponding to the data you want to process. You may list multiple source files to process in the same command. Remember that you must put the data in `raw` if you do not provide a `url` key in the source file! Optional arguments are listed in the table below.

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

The command line usage information can be printed in terminal by entering

```
$ opentab --help
```

#### Example use

For the examples below, the current working directory is `~` (or `$HOME`) and we have source files `SOURCE1.json` and `SOURCE2.json` stored in `sources` in the initialized OpenTabulate directory.

Basic use:

```
$ opentab .opentabulate/sources/SOURCE1.json
```

Run `opentab` using two CPU cores without downloading data from URLs:

```
$ opentab -j 2 -u .opentabulate/sources/SOURCE1.json .opentabulate/sources/SOURCE2.json
```

Test for correct syntax of source file:

```
$ opentab --ignore-proc .opentabulate/sources/SOURCE1.json
```
