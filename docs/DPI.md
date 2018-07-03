## Writing source files 

For the data set maintainer, this is a short guide on how to write source files or *data processing instructions*. First some terminology and remarks. The source files are written in JSON format, where specified key-value pairs serve as metadata for the data processing and cleaning. We refer to a key-value pair as a *tag*. Some keys may contain a list of key-value pairs, such as `address` containing key-value pairs for `city`, `postcode` and so forth.

The values entered must be what the dataset identifies the key to be. To illustrate what is meant by this, let's say you have a dataset in CSV format with a column named `BusinessName`. The key `name` is associated with business names, so you must write `"name" : "BusinessName"` in the source file.

For explicit examples of source files of small datasets, see the `examples` folder. The rest of this documentation describes the source file formatting and available/required tags.

### Dataset tag

The following tags are **required** for the scripts to run. Without the proper specification, the processing script will print an error alerting you of it's distaste with your provided source file or throw an error.

| Tag | Description | Requirement |
| --- | ----------- | ----------- |
| `filename` | The filename of the dataset. | Must be added if `url` is not provided. Otherwise, do not add. |
| `url` | The direct URL of the dataset. | Must be added if `filename` is not provided. Otherwise do not add. |
| `type` | The file format of the dataset. | Required. |
| `header` | The dataset's identifier for a business entity. For example, a _tag_ in XML format that identifies a business entity has metadata tags from `info` such as address, phone numbers, names, and so forth. The name of this tag is what should be entered for `header`. | Required if in XML format. | 
| `info` | Metadata of the data contents, such as addresses, names, etc. | Required. |

### Info tag

| Tag | Description | Requirement |
| --- | ----------- | ----------- |
| `name` | Business name. | Required |
| `industry` | Business industry type. _Might be replaced with NAICS standard_. |  |
| `address` | Address metadata, such as street number, street name, postal code, etc. |  |
| `phone` | Business phone number. |  |
| `email` | Business e-mail. |  |
| `website` | Business website URL. |  |
| `longitude` | Location refering to the geographic coordinate system. |  |
| `latitude` | Location refering to the geographic coordinate system. |  |

### Address tag

| Tag | Description | Requirement |
| --- | ----------- | ----------- |
| `house_number` | Street number. |  |
| `road` | Street name. |  |
| `unit` | Unit number. |  |
| `city` | City name. |  |
| `region` | Province/terrority name. |  |
| `country` | Country name or code. |  |
| `postcode` | Postal code. |  |

### Default tag
| Tag | Description | Requirement |
| --- | ----------- | ----------- |
| `city` | City name. |  |
| `region` | Province/terrority name. |  |
| `country` | Country name or code. |  |
