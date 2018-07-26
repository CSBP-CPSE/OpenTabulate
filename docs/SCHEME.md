# Data processing and cleaning scheme

### OpenBusinessRepository directory '.'
| Path | Description |
| ---- | ----------- |
| `./docs/` | OpenBusinessRepository documentation |
| `./sources/` | Source files are stored here under any folder hierarchy you wish. |
| `./tools/` | OpenBusinessRepository's core data processing and cleaning scripts reside here | 
| `./scripts/` | User-made preprocessing and postprocessing scripts are stored here **(NOT AVAILABLE)** | 
| `./testing/` | Experimental scripts and items are added here. These are not integrated with the scripts in `./tools` |
| `./pdctl` | Interactive data processing script | 
| `./README.md` | General information about the project | 
| `./obr-init.py` | Python script to initialize the data processing directory |

### obr-init.py

When running this script, the following folder tree is created:
```
./pddir/
├── raw/
├── pp/
├── dirty/
└── clean/
```
| Path | Description |
| ---- | ----------- |
| `raw` | source datasets should be stored here, noting that if your dataset is specified by `url` in a source file, it will be downloaded to this directory |
| `pp` | preprocessing directory, raw datasets are copied here when data processing begins |
| `dirty` | datasets from `pp` are sent here after being reformatted to a standardized CSV format |
| `clean` | datasets are sent here after cleaning |

### Tools directory './tools/'

| Path | Description |
| ---- | ----------- |
| `char_encode_check.py` | Detect character encoding heuristically |
| `data_parser.py` | Data parsing tools for different file formats |
| `process.py` | Backend for `pdctl` |
| `src_check.py` | Check integrity of source file (eg. does the data file exist?) |
| `src_fetch_url.py` | Fetch URL from source file |
| `src_parser.py` | Parse and error-check source file |
