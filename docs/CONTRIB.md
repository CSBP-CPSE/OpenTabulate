## Writing source files 

For the data set maintainer, this is a short guide on how to write source files or *data processing instructions*. First some terminology and remarks. The source files are written in JSON format with the `.json` file extension in the file name. The specified JSON key-value pairs serve as metadata for the data processing and cleaning. We refer to a key-value pair as a *tag*. Some keys may contain a list of key-value pairs, such as `address` containing key-value pairs for `city`, `postcode` and so forth.

The values entered must be what the dataset identifies the key to be. To illustrate what is meant by this, let's say you have a dataset in CSV format with a column named `BusinessName`. The key `name` is associated with business names, so you must write `"name" : "BusinessName"` in the source file.

For explicit examples of source files of small datasets, see the `examples` folder. The rest of this documentation describes the source file formatting and available/required tags.

## Tags

### Dataset tags

| Key | JSON Type | Description | Required? | Dependencies |
| --- | --------- | ----------- | --------- | ------------ |
| `file` | string | Name of the local data file residing in `./pddir/raw/` to process. | Yes | None. |
| `url` | string | A URL string giving the direct link to the data set. | No | Requires `file`, which defines what the URL link should be named to. _Does not currently support archive URLs (eg. ZIP)_. |
| `format` | string | Dataset file format. Currently supports `csv` and `xml`. | Yes | None. |
| `encoding` | string | Dataset character encoding, which can be "utf-8", "cp1252", or "cp437". If not specified, the encoding is guessed from this list. | No | None. |
| `header` | string | Identifier for a business entity. For example, a _tag_ in XML format that identifies a business entity has metadata tags from `info` such as address, phone numbers, names, etc. The name of this tag is what should be entered for `header`. | Yes, except for CSV format | None. |
| `info` | object | Metadata of the data contents, such as addresses, names, etc. | Yes | None. |
| `force` | object | Metadata prompted to be overwritten to the given value of a key, regardless of the datasets interpretation of that key. For example, if all business entities reside in the province of Ontario, one defines a tag in `force` by `"prov": "ON"`. | No | None. |

### Info tags

The tag `info` is defined as a JSON object. Its possible tags are listed below.

| Key | JSON Type | Description | Required? | Dependencies |
| --- | --------- | ----------- | --------- | ------------ |
| `bus_name` | string/list | Business (legal) name. | No | None. |
| `trade_name` | string/list | Trade name. | No | None. |
| `bus_type` | string/list | Business type. | No | None. |
| `bus_no` | string/list | Business number or identifier, e.g. roll number. | No | None. |
| `bus_desc` | string/list | Business description. | No | None. |
| `lic_type` | string/list | Business licence type. | No | None. |
| `lic_no` | string/list | Business license number. | No | None. |
| `bus_start_date` | string/list | Start date of business. | No | None. |
| `bus_cease_date` | string/list | Closure date of business. | No | None. |
| `active` | string/list | Closure date of business. | No | None. |
| `full_addr` | string/list | Full address of business (concatenated street name, number, etc.) | No | Cannot be used together with `address`. |
| `address` | object | Address metadata, such as street number, street name, postal code, etc. | No | Cannot be used together with `full_addr`. |
| `phone` | string/list | Business phone number. | No | None. |
| `fax` | string/list | Business fax number. | No | None. |
| `email` | string/list | Business e-mail. | No | None. |
| `website` | string/list | Business website. | No | None. |
| `tollfree` | string/list | Business toll-free number. | No | None. |
| `comdist` | string/list | Community, district or neighbourhood name. | No | None. |
| `region` | string/list | Region name (_not_ province) | No | None. |
| `longitude` | string/list | Location refering to the geographic coordinate system. | No | None. |
| `latitude` | string/list | Location refering to the geographic coordinate system. | No | None. |
| `no_employed` | string/list | Number of employees. | No | None. |
| `no_seasonal_emp` | string/list | Number of seasonal employees. | No | None. |
| `no_full_emp` | string/list | Number of full-time employees. | No | None. |
| `no_part_emp` | string/list | Number of part-time employees. | No | None. |
| `emp_range` | string/list | Total number of employees range. | No | None. |
| `home_bus` | string/list | Is this a home business? | No | None. |
| `munic_bus` | string/list | Is this a municipal business? | No | None. |
| `nonres_bus` | string/list | Is this a non-residential business? | No | None. |
| `exports` | string/list | Does this business export? | No | None. |
| `exp_cn_X` | string/list | (X=1,2,3) Export country. | No | None. |
| `naics_X` | string/list | (X=2,3,4,5,6) NAICS X-digit code. | No | None. |
| `naics_desc` | string/list | NAICS word description. | No | None. |
| `qc_cae_X` | string/list | (X=1,2) Quebec establishment economic activity code. | No | None. |
| `qc_cae_desc_X` | string/list | (X=1,2) Quebec establishment economic activity description. | No | None. |
| `facebook` | string/list | Business Facebook page. | No | None. |
| `twitter` | string/list | Business Twitter account. | No | None. |
| `linkedin` | string/list | Business LinkedIn. | No | None. |
| `youtube` | string/list | Business YouTube channel. | No | None. |
| `instagram` | string/list | Business Instagram account.  | No | None. |


### Address tag

| Key | JSON Type | Description | Required? | Dependencies |
| --- | --------- | ----------- | --------- | ------------ |
| `house_number` | string/list | Street number.  | No | Contained in `address` object. |
| `road` | string/list | Street name (and direction).  | No | Contained in `address` object. |
| `unit` | string/list | Unit number.  | No | Contained in `address` object. |
| `city` | string | City name.  | No | Contained in `address` object. |
| `prov` | string | Province/territory name.  | No | Contained in `address` object. |
| `country` | string | Country name.  | No | Contained in `address` object. |
| `postcode` | string/list | Postal code.  | No | Contained in `address` object. |

### Force tag
| Key | JSON Type | Description | Required? | Dependencies |
| --- | --------- | ----------- | --------- | ------------ |
| `city` | string | City name. | No | None. |
| `region` | string | Province/terrority name. | No | None. |
| `country` | string |  Country name. | No | None. |

## Source file features

### Precautions

To not run into issues and in the spirit of having clean and readable source files

- do not add empty strings or null, i.e. `""`, as a value for a key
- do not add empty lists or empty objects
- if a key is in the source file, there should be only one such key

### List concatenation

When writing tags, some keys above support having JSON lists as a value. For example

```javascript
	...
	"full_addr": ["Address Line 1", "Address Line 2", "Address Line 3"],
	...
```

Since address lines are not supported keys and some datasets will only provide this information for an address, we want it incorporated in our data somehow. Lists are interpreted by the processing scripts as an ordered entry concatentation. For example, if a dataset has the entry and columns

```
Business Name, ..., Address Line 1, Address Line 2, Address Line 3, ...
...
"JOHN TITOR TIME MACHINES", ..., "2036 STEINS GATE", "CANADA", "T5T 5R5", ...
...
```

then the source file and data processing script will produce the entry

```
"bus_name", ..., "full_addr", ...
...
"JOHN TITOR TIME MACHINES", ..., "2036 STEINS GATE CANADA T5T 5R5", ...
... 
```
