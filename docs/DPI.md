### Writing source files 

For the data set maintainer, this is a short guide on how to write source files or *data processing instructions*. The source files are written in JSON format, where specified key-value pairs serve as metadata for the data processing and clean. We refer to a key-value pair as a *tag*. The keys are standardized and the corresponding values must reflect that of your datasets without error, or the scripts won't process your data! 

###### Structure metadata

The following tags are **required** for the scripts to run. Without the proper specification, the processing script will print an error alerting you of it's distaste with your provided source file or throw an error.

| Tag | Description | Requirement |
| --- | ----------- | ----------- |
| `filename` | The filename of the dataset. | Must be added if `url` is not provided. Otherwise, do not add. |
| `url` | The direct URL of the dataset. | Must be added if `filename` is not provided. Otherwise do not add. |
| `type` | The file format of the dataset. | Required. |
| `info` | Metadata of the data contents, such as addresses, names, etc. | Required. |

###### Info tag

...