## Writing source files 

For the dataset contributor or OBR user, this is a guide on how to write source files or *data processing instructions*. First some terminology and remarks. The source files are written in JSON format with the `.json` file extension in the filename. Each JSON key-value pair serves as metadata for the data processing software, which in the end produces a CSV file whose column names are the corresponding keys. The values dictate the row entries below the first row.

We refer to a key-value pair as a *tag*. Some keys may contain a list of key-value pairs, such as `address` containing key-value pairs for `city`, `postcode` and so forth. Here is an example of a source file for Vancouver business licenses.

```javascript
{
    "localfile": "bc-vancouver.csv:business_licences.csv",
    "format": "csv",
    "url": "ftp://webftp.vancouver.ca/OpenData/csv/business_licences_csv.zip",
    "localarchive": "bc-vancouver.zip",
    "compression": "zip",
    "info": {
		"bus_name": "BusinessName",
		"bus_type": "BusinessType",
        "trade_name": "BusinessTradeName",
		"lic_no": "LicenceNumber",
		"no_employed": "NumberOfEmployees",
		"address": {
			"house_number": "House",
			"road": "Street",
			"unit": "Unit",
			"city": "City",
			"prov": "Province",
			"country": "Country",
			"postcode": "PostalCode"
		},
		"latitude": "Latitude",
		"longitude": "Longitude",
		"comdist": "LocalArea"
    }
}
```

The values entered for each key are the field names of your dataset. Each of the string values in the Vancouver source file correspond to a column name in the dataset, where the original data is in CSV format. To get started, first, say your dataset is in CSV format and in the first row we have the fields

```
BusinessNumber, BusinessName, CivicAddress, PostalCode, ...
```

You would infer from the data below or the data collection methodology to associate `BusinessNumber` with the key `bus_no`. Hence, part of your source file should contain the line `"bus_no" : "BusinessNumber"`. If you face a dilemma of which key to select, you may have to consult with the data provider or methodology for clarity on what the fields refer to. You may also recommend us to add new keys!

If your dataset is in XML format, each entity might have a XML tag of the form

```xml
	<URL>http://www.mybusinesswebsite.com/home.htm</URL>
```

Thus, part of your source file should contain the line `"website": "URL"`. Many more examples of source files are found in `./sources/`.

## Tag documentation

### Dataset tags

The following tags are for dataset properties and naming. These tags must appear in the first set of curly braces `{...}` of the source file.

| Key | JSON Type | Description | Required? | Dependencies |
| --- | --------- | ----------- | --------- | ------------ |
| `localfile` | string | The (desired) name of the local data file stored in `./pddir/raw/` to process. If the data is in an archive, as specified by `localarchive`, you may specify the `localfile` string as `"desired_localfile_name:data_filename_given_in_archive"`. If no colon is used, the software assumes `localfile` to be both the name of the file in the archive and the desired name of the local data copy. | Yes | None. |
| `localarchive` | string | The (desired) name of the local archive (e.g. `zip`, `tar`) stored in `./pddir/raw/`. | No | Requires `compression`. |
| `url` | string | A URL string giving the direct link to the data set. | No | Requires `localfile`. Also requires `localarchive` and `compression` if the URL refers to an archive download. |
| `format` | string | Dataset file format. Currently supports `csv` and `xml`. | Yes | None. |
| `compression` | string | **(EXPERIMENTAL)** The compression algorithm for the archive containing your dataset. Currently supports `zip`. | No | None. | 
| `encoding` | string | Dataset character encoding, which can be "utf-8", "cp1252", or "cp437". If not specified, the encoding is guessed from this list. | No | None. |
| `pre` | string/list | **(EXPERIMENTAL)** A path or list of paths to run preprocessing scripts. | No | None. |
| `header` | string | Identifier for an entity in XML. For example, a XML tag that identifies a business entity has metadata tags from `info` such as address, phone numbers, names, etc. The name of this tag is what should be entered for `header`. | Yes, except for CSV format. | None. |
| `info` | object | Metadata of the data contents, such as addresses, names, etc. | Yes | None. |
| `force` | object | Metadata prompted to be overwritten to the given value of a key, regardless of the datasets interpretation of that key. For example, if all business entities reside in the province of Ontario, one can "force" all entities to have "Ontario" as their `prov` entry. | No | None. |

### info tags

The tag `info` is defined as a JSON object, which is another set of curly braces `"info": {...}`. Its possible tags are listed below.

##### General info tags

| Key | JSON Type | Description | Required? | Dependencies |
| --- | --------- | ----------- | --------- | ------------ |
| `full_addr` | string/list | Full address of business (concatenated street name, number, etc.). Note: the entries for this key will be subjected to an address parser! | No | Cannot be used together with `address`. |
| `address` | object | Address metadata, such as street number, street name, postal code, etc. | No | Cannot be used together with `full_addr`. |
| `phone` | string/list | Business phone number. | No | None. |
| `fax` | string/list | Business fax number. | No | None. |
| `email` | string/list | Business e-mail. | No | None. |
| `website` | string/list | Business website. | No | None. |
| `tollfree` | string/list | Business toll-free number. | No | None. |
| `comdist` | string/list | Community, district or neighbourhood name. | No | None. |
| `region` | string/list | Region name (_not_ province). | No | None. |
| `longitude` | string/list | Location refering to the geographic coordinate system. | No | None. |
| `latitude` | string/list | Location refering to the geographic coordinate system. | No | None. |

##### Business info tags

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
| `facebook` | string/list | Facebook page. | No | None. |
| `twitter` | string/list | Twitter account. | No | None. |
| `linkedin` | string/list | LinkedIn. | No | None. |
| `youtube` | string/list | YouTube channel. | No | None. |
| `instagram` | string/list | Instagram account.  | No | None. |

### (NOT CURRENTLY AVAILABLE) Education facility info tags 

| Key | JSON Type | Description | Required? | Dependencies |
| --- | --------- | ----------- | --------- | ------------ |
| `ins_name` | string/list | Education institution name (or simply school name). | Yes | None. |
| `ins_type` | string/list | Education institution type (public, private, etc.) | No | None. |
| `edu_level` | string/list | Education level (elementary, secondary, post-secondary, etc.) | No | None. |
| `board_name` | string/list | School board name or district name. | No | None. |
| `school_yr` | string/list | **(EXPERIMENTAL)** School year of the education facility data. The most recent year is processed. | No | None. |

### Address info tag

The `address` tag is a JSON object defined inside `info`. Note that this cannot be used simultaneously with `full_addr`, since the latter invokes an address parser, whereas this tag is reserved for datasets that have already separated the address tokens.

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

The `force` tag is a JSON object. It is special in that the value of a key in `force` overrides every entry of the resulting CSV column defined by key, by overwriting it with the corresponding value. For example, placing

```javascript
	"force": { 
		"country": "canada"
	}
```

into your source file will insert the column `country` during data processing and fill in every entry with "canada". This object supports the following keys:

| Key | JSON Type | Description | Required? | Dependencies |
| --- | --------- | ----------- | --------- | ------------ |
| `city` | string | City name. | No | None. |
| `prov` | string | Province/terrority name. | No | None. |
| `country` | string |  Country name. | No | None. |

## Source file features and remarks

### Precautions!

To not run into issues and in the spirit of having clean and readable source files

- do not add empty strings or null, i.e. `""`, as a value for a key
- do not add empty lists or empty objects
- if a key is in the source file, there should be only one such key

To prevent some of these practices, preventing the above in the source file parsing scheme will be considered in the future.

### List concatenation

When writing tags, some keys above support having JSON lists as a value. For example

```javascript
	...
	"key": ["value1", "value2", "value3"],
	...
```

OBR interprets this as "for each entity in the data to process, an entity with a field under the column `key` is produced with all the original entries for `value1`, `value2`, and `value3` concatenated". To put it another way, lists are interpreted by the processing scripts as ordered entry concatentation.

A common use of this feature is for addresses. Since address lines are not supported keys and some datasets will only provide this information for an address, we want it incorporated in our data somehow. For example, if a dataset has the entry and columns

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

midway through the data processing. If the key was *not* `full_addr` and supported lists, the above entry appears in the final CSV file at the end of processing. For the example above, a slight technicality with `full_addr` is that it gets fed into an address parser.
