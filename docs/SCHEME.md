# Data processing and cleaning scheme

### OpenBusinessRepository directory '.'
| Path | Description |
| ---- | ----------- |
| `./docs/` | OpenBusinessRepository documentation |
| `./sources/` | Source files are stored here under any folder hierarchy you wish. |
| `./tools/` | OpenBusinessRepository's core data processing and cleaning scripts reside here | 
| `./scripts/` | User-made preprocessing and postprocessing scripts are stored here **(NOT AVAILABLE)** | 
| `./testing/` | Experimental scripts and items are added here. These are not integrated with the production system (i.e. `./tools`) |
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

### pdctl.py

The main interface for the production system is the `pdctl.py` interactive script. The workflow of processing a single source is structured relatively simply by reading the Python scripts, however, it is summarized here for the reader.

#### 1. parse the source file

The first step as defined in `process.py` is to parse the given source file. If the JSON syntax is correct, the `json` module will load the source file as a `dict` object. The semantics are then checked as defined in `CONTRIB.md`. Afterwards, if `url` is specified as a tag, the process will attempt to fetch the URL and download it to the `raw` directory in the `pddir` folder tree. If this fails, an existence test for a fallback dataset is checked.

#### 2. csv standardization

The next step is to convert the dataset into CSV format with our own choice of column names. This is handled by `data_parser.py`. Minor data cleaning is applied before or during this standardization process, depending on dataset's original format.

*Before*
+ **Character decoding.** Much of the scripts work with strings, so the dataset has to be decoded from the correct (or at least valid) encoding. In the unfortunate situation where no encoding metadata is provided or is missing, the character encoding is guessed from a small list of commonly used Latin character sets.
+ **Byte order mark removal.** (CSV) Some datasets possess a BOM at the start of the file, which may conflict with datasets in CSV format if the first column is referenced in the source file.
+ **Missing fields.** (CSV/XML) Poorly formatted datasets will contain logically missing entries (not blank entries). For example, a CSV file with 12 columns, but one row has 10. Depending on the dataset format, these are corrected by being ignored or appended with blanks.

*Concurrent*
+ **Address parsing.** If the `full_addr` tag is used, `libpostal` will be used to parse and split the address into our specified fields, e.g. `road`, `house_number`, `unit`, and so on.
+ **Regex scrubbing.** Some data cleaning is handled easily using regular expressions, so this is taken advantage of during the CSV standardization. All entries are made lower case as well.

#### 3. cleaning

-- N/A --

*Additional remark*. To improve efficiency, columns not included in the source file are added at the very ended. The corresponding entries will consist of all blanks for every row, since these were not given in the source file.


### Remarks

As stated in `README.md`, much of the code is being ported to a central Python script containing classes and methods that interpret the production system as an object-oriented model. Our methodlogy such as the parsing, standardization, and cleaning will not change. The interface `pdctl.py` will utilize the class and method definitions using the same workflow.
