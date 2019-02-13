# Writing source files

A fundamental component of OpenTabulate and its use to tabulate your data is the *source file*. A source file is a short metadata file in JSON format that acts as a "configuration file", to give the necessary information for OpenTabulate to do data processing on a specific dataset. Such information includes the original dataset format, which attribute names in the original data get mapped to, the name of the dataset on the disk, and so on.

We refer to a JSON key-value pair as a *tag*. Some keys may contain a list of key-value pairs, such as `address` containing key-value pairs for `city`, `postcode` and so forth. 

---

#### Example 

Source files follow a specific format for OpenTabulate to parse. Before presenting the proper use, nuances, and documentation, we present an example. Below is a source file for a business register dataset for Kitchener in Ontario, Canada.

```
{
    "localfile": "on-kitchener.csv",
    "url": "https://opendata.arcgis.com/datasets/9b9c871eafce491da8a3d926a8a44ef2_0.csv",
    "format": "csv",
    "database_type": "business",
    "info": {
		"bus_name": "COMPANY_NAME",
		"bus_no": "ID",
		"bus_desc": "PROFILE",
		"address" : {
			"street_no": "STREET_NUMBER",
			"street_name": "STREET_NAME",
			"unit": "UNIT",
			"postcode": "POSTAL_CODE"
		},
		"latitude": "Y",
		"longitude": "X",
		"no_employed": "TOTAL_EMPLOYEES"
    }
}
```

The keys within the first pair of curly braces are `localfile`, `url`, `format`, `database_type`, and `info`. Besides `info`, tags that occur in this layer are intended for file handling. 

- `localfile`  represents the name of the file (to be) stored locally to the disk. 
- `url` defines the download link for the dataset.
- `format` tells OpenTabulate what the dataset's original format is, so as to choose the appropriate algorithms.
- `database_type` describes which data attribute names will be considered under `info`

The `info` tag contains "attribute mapping" information. OpenTabulate's job is to reformat your data into a tabular format, but you must specify where and which data (from the original dataset) appears in the tabulated data. Consider `on-kitchener.csv` which has a column with the attribute name `COMPANY_NAME`. From consultation with the data provider or by intuition, you determine that this column holds legal business names. This best aligns with the key `bus_name`, which is a column name for the eventually tabulated data. The remaining tags in `info` are determined by a similar methodology with reference to the different keys documented below. 

---

# Tag documentation

This section is ordered to match the format in the example above. The five attributes of each tag table are defined in the bullets below.

- **Key** : Key name and column name for the tabulated data.
- **JSON Type** : The supported JSON type for the key's value.
- **Description** : A brief description of the what the key represents.
- **Required?** : Defines whether or not the given key and value *must* be included in a source file.
- **Dependencies** : Defines what other keys *must* be included if you use the given key.

### File handling tags

The following tags are generally for data file handling and naming. These tags must appear in the first set of curly braces `{...}` of the source file.

| Key | JSON Type | Description | Required? | Dependencies |
| --- | --------- | ----------- | --------- | ------------ |
| `localfile` | string | The (desired) name of the local data file stored in `./pddir/raw/` to process. If the data is in an archive, as specified by `localarchive`, you may specify the `localfile` string as `"desired_localfile_name:data_filename_in_archive"`. If no colon is used, OpenTabulate assumes `localfile` to be both the name of the file in the archive and the desired name of the local data copy. | Yes | None. |
| `localarchive` | string | The (desired) name of the local archive (e.g. `zip`, `tar`) stored in `./pddir/raw/`. | No | Requires `compression`. |
| `url` | string | A URL string giving the direct link to the data set. | No | Requires `localarchive` and `compression` if the URL refers to an archive download. |
| `format` | string | Dataset file format. Currently supports `csv` and `xml`. | Yes | None. |
| `database_type` | string | Dataset type to define which `info` tags to use. Currently supports `business`, `education`, `hospital`, and `library`. | Yes | None. |
| `compression` | string | The compression algorithm for the archive containing your dataset. Currently supports `zip`. | No | None. | 
| `encoding` | string | Dataset character encoding, which can be "utf-8", "cp1252", or "cp437". If not specified, the encoding is guessed from this list. | No | None. |
| `pre` | string/list | A path or list of paths to run pre-processing scripts. | No | None. |
| `post` | string/list | A path or list of paths to run post-processing scripts. | No | None. |
| `header` | string | Identifier for an entity in XML. For example, a XML tag that identifies a business entity has metadata tags from `info` such as address, phone numbers, names, etc. The name of this tag is what should be entered for `header`. | Yes, except for CSV format. | None. |
| `info` | object | Metadata of the data contents, such as addresses, names, etc. | Yes | None. |

### info tags

The tag `info` is defined as a JSON object, which is another set of curly braces `"info": {...}`.

#### General info tags

These keys can be used for any `database_type`. Currently, all of them refer to non-address location and contact information.

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
| `region` | string/list | Region name (_not_ province or territory). | No | None. |
| `longitude` | string/list | Location refering to the geographic coordinate system. | No | None. |
| `latitude` | string/list | Location refering to the geographic coordinate system. | No | None. |

#### Business info tags

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

#### Education facility info tags 

| Key | JSON Type | Description | Required? | Dependencies |
| --- | --------- | ----------- | --------- | ------------ |
| `ins_name` | string/list | Institution name (or school name). | No | None. |
| `ins_type` | string/list | Institution type (public, private, etc.) | No | None. |
| `ins_code` | string/list | Institution code (note: usually specific to the data provider) | No | None. |
| `edu_level` | string/list | Education level (elementary, secondary, post-secondary, etc.) | No | None. |
| `board_name` | string/list | School board or district name. | No | None. |
| `board_code` | string/list | School board name or district code. (note: usually specific to the data provider) | No | None. |
| `school_yr` | string/list | School year attributed to the data entry. | No | None. |
| `range` | string/list | Education level range (e.g. K-12). | No | None. |
| `ecs` | string/list | Early childhood services? (binary output)\* | No | None. |
| `kindergarten` | string/list | Kindergarten? (binary output)\* | No | None. |
| `elementary` | string/list | Elementary education? (binary output)\* | No | None. |
| `middle` | string/list | Lower secondary education? (binary output)\* | No | None. |
| `secondary` | string/list | Upper secondary education? (binary output)\* | No | None. |
| `post-secondary` | string/list | Post-secondary education? (binary output)\* | No | None. |

\* These categories were chosen with respect to [ISCED](https://en.wikipedia.org/wiki/International_Standard_Classification_of_Education) (Internation Standard Classification of Education).

#### Hospital info tags 

| Key | JSON Type | Description | Required? | Dependencies |
| --- | --------- | ----------- | --------- | ------------ |
| `hospital_name` | string/list | Name of hospital or health centre. | No | None. |
| `hospital_type` | string/list | Type of health centre (e.g. Community Hospital, Community Health Centre, etc.) | No | None. |
| `health_authority` | string/list | Regional governing health authority. | No | None. |
| `hours` | string/list | Hours of service | No | None. |
| `county` | string/list | County or region. | No | None. |

#### Library info tags 

| Key | JSON Type | Description | Required? | Dependencies |
| --- | --------- | ----------- | --------- | ------------ |
| `library_name` | string/list | Library name. | No | None. |
| `library_type` | string/list | Library type (depends on the provider, example values are branch or head, or municipal). | No | None. |
| `library_board` | string/list | Name of governing library board. | No | None. |
| `hours` | string/list | Hours of service | No | None. |
| `county` | string/list | County or region | No | None. |

#### Address info tag

The `address` tag is a JSON object defined inside `info`. Note that this cannot be used simultaneously with `full_addr`, since the latter invokes an address parser, whereas this tag is reserved for datasets that have already separated the address tokens.

| Key | JSON Type | Description | Required? | Dependencies |
| --- | --------- | ----------- | --------- | ------------ |
| `street_no` | string/list | Street number.  | No | Contained in `address` object. |
| `street_name` | string/list | Street name, type, and direction.  | No | Contained in `address` object. |
| `unit` | string/list | Unit number.  | No | Contained in `address` object. |
| `city` | string | City name.  | No | Contained in `address` object. |
| `prov/terr` | string | Province/territory name.  | No | Contained in `address` object. |
| `country` | string | Country name.  | No | Contained in `address` object. |
| `postcode` | string/list | Postal code.  | No | Contained in `address` object. |

## Source file syntax features and nuances

### List concatenation

When writing tags, some keys above support having JSON lists as a value. For example

```javascript
	...
	"key": ["value1", "value2", "value3"],
	...
```

OpenTabulate interprets this as "for each entity in the data to process, concatenate (with separation by spaces) all of the data in the entity under the attributes `value1`, `value2`, and `value3` (in that order) to be processed and output to an entry under `key`. 

A common use of this feature is for addresses. Since address lines are not supported keys and some datasets will only provide information in this manner for an address, we still want to tabulate the data. For example, if a dataset has the entry and columns

```
Business Name, ..., Address Line 1, Address Line 2, Address Line 3, ...
...
"JOHN TITOR TIME MACHINES", ..., "2036 STEINS GATE", "CANADA", "T5T 5R5", ...
...
```

then the source file and data processing script will process the entry 

```
"2036 STEINS GATE CANADA T5T 5R5"
```

for `"JOHN TITOR TIME MACHINES"` in whatever way `full_addr` is handled. In this case, `full_addr` uses an address parser, and will parse the concatenated entry above.

### force - manually inject or overwrite data

Any string-valued tags or nested tags in `info` support what we call the `force` value. A `force` value defines or "forces" user-defined content for the associated key in the tabulated data\*. A few situations in which this may be helpful are:

- The dataset to process represents a particular city or province, say Winnipeg and Manitoba, but the data does not explicitly have the city and province for any entity in the data. If we want to include the city or province information in the tabulated data, we can let OpenTabulate do this automatically by writing `"city": "force:Winnipeg"` and `"prov/terr": "force:Manitoba"` in the source file. The resulting tabulated data will have columns `city` and `prov/terr` with the corresponding values in each row.
- A dataset on public schools does not describe its own institution type (namely, that the schools are public). Adding `"ins_type": "force:public"` to the source file means OpenTabulate will generate a tabulated dataset with an `ins_type` column with `public` in all of its entries.
- The address parser you're using is more accurate with additional data that may not be explicitly in the dataset. For example, we may have a XML file with a `<CivicAddress>` XML tag that contains the street number, name, city, and province, a separate `<PostalCode>` XML tag, and no tags for the country. If you know your data resides in Canada, you can write `"full_addr": ["CivicAddress", "force:Canada", "PostalCode"]"` to inject "Canada" into the list-concatenated address before running it through the address parser.

The general syntax is `"key": "force:content_to_inject"` for `info` keys that support string values.

(\*) User-defined content under `force` applies *after* pre-processing and *before* OpenTabulate's regular processing.

### Debugging syntax errors

OpenTabulate checks the syntax of your source file and will warn you if something is off, but this checking does not cover all situations. Moreover, it cannot make sense of logical errors until either during processing or when you inspect the tabulated data. 

Before posting a question or issue, check this [GitHub issue](https://github.com/CSBP-CPSE/OpenTabulate/issues/12) for clues to erroneous output or functionality.
