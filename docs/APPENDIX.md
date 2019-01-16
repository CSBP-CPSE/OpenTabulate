# Appendix

#### OpenBusinessRepository directory

| Path | Description |
| ---- | ----------- |
| `docs/` | OpenBusinessRepository documentation |
| `sources/` | Source files are stored here under any folder hierarchy you wish. |
| `scripts/` | User-made preprocessing and postprocessing scripts are stored here.  | 
| `tools/` | OpenBusinessRepository's core data processing and cleaning scripts reside here. | 
| `README.md` | General information about the project. | 

#### Initialize flag and directories

Running the `--initialize` flag for `obrpdctl.py` generates the following directory tree in your cloned directory:

```
pddir/
├── raw/
├── pp/
├── dirty/
└── clean/
```

The functionality of having these directories are described in the table below.

| Path | Description |
| ---- | ----------- |
| `raw` | Source datasets should be stored here, noting that if your dataset is specified by `url` in a source file, it will be downloaded to this directory. |
| `pp` | **(DEPRECATED)** Preprocessing directory, raw datasets are copied here when data processing begins. |
| `dirty` | Datasets from ~~`pp`~~ `raw` are sent here during processing. They represent datasets converted to CSV format that have not been cleaned yet. |
| `clean` | Datasets are sent here after cleaning. |

#### Program workflow

The main interface for the production system is the `obrpdctl.py` interactive script. The workflow of processing source files is summarized in the following chart. Hopefully this is a good reference when inspecting the source code.

![Workflow](docs/workflow.png)

#### Current key features

+ **Downloading data.** The data can be referenced by a URL to be retrieved. The data can also be compressed or archived.
+ **Character encoding handler.** In the event that no encoding is provided, a class method is used to check for a valid decoding in a linear order based on the data (e.g. Canadian data will likely involve Latin character sets).
+ **Byte order mark removal.** Some datasets possess a byte order mark at the start of the file, which sometimes conflicts with our software if kept.
+ **Missing field handler.** Poorly formatted datasets will contain missing (*not blank*) entries. Our code handles this appropriately depending on the dataset format. For example, for a poorly formatted CSV file, the erroneous row is deleted.
+ **Address parsing support.** If the `full_addr` tag is used, `libpostal` will be used to parse and split the address into `road`, `house_number`, and so on.
+ **Regex scrubbing.** Easy to handle residual characters or dirty entries, such as whitespace, is cleaned using regular expressions.

