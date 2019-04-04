# Introduction and features

OpenTabulate is open-source software designed to centralize, process, and clean data. It is inspired by projects such as OpenAddresses and is designed to reformat, clean, and tabulate data. The code for the OpenTabulate API resides in `tools/opentabulate.py` and is interfaced by the command-line tool `tabctl.py`.

### Key features

+ **Downloading Data.** The data can be referenced by a URL to be retrieved. The data can also be compressed or archived.
+ **Tabulation.** Convert data into CSV format with a common set of column names for easy merging.
+ **Pre/post processing scripts.** If OpenTabulate is missing a feature, you can fill in the gap by customizing and automating processing before and after OpenTabulate's tabulation and cleaning.
+ **Entry Filtering.** You can tabulate a subset of the data by regular expression filtering. All regular expressions must find a match in their corresponding attributes in order to mark the data entity for processing.
+ **Regex Cleaning and Error Filtering.** Easy to handle residual characters or dirty entries, such as whitespace and unneeded punctuation, is cleaned using regular expressions. Structured information such as province names, postal codes and phone numbers are reformatted if it matches the standard definition, and is otherwise filtered into an "error" file.
+ **Optional Address Parsing Support.** If the `full_addr` tag is used, `libpostal` will be used to parse and split the address into `road`, `house_number`, and so on.

### Technical nuances

+ **Character Encoding Handler.** In the event that no encoding is provided, a class method is used to check for a valid decoding in a linear order based on the data (e.g. Canadian data will likely involve Latin character sets).
+ **Byte order mark removal.** Some datasets possess a byte order mark at the start of the file, which sometimes conflicts with our software if kept.
+ **Missing field handler.** Poorly formatted datasets will contain missing (*not blank*) entries. Our code handles this appropriately depending on the dataset format. For example, for a poorly formatted CSV file, the erroneous row is deleted.
