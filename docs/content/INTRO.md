# Introduction and features

OpenTabulate is open-source software designed to centralize, process, and clean data. It is inspired by projects such as OpenAddresses and is designed to reformat, clean, and tabulate data. The code for the OpenTabulate API resides in `tools/opentabulate.py` and is interfaced by the command-line tool `tabctl.py`.

### Key features

+ **Downloading data.** The data can be referenced by a URL to be retrieved. The data can also be compressed or archived.
+ **Character encoding handler.** In the event that no encoding is provided, a class method is used to check for a valid decoding in a linear order based on the data (e.g. Canadian data will likely involve Latin character sets).
+ **Byte order mark removal.** Some datasets possess a byte order mark at the start of the file, which sometimes conflicts with our software if kept.
+ **Missing field handler.** Poorly formatted datasets will contain missing (*not blank*) entries. Our code handles this appropriately depending on the dataset format. For example, for a poorly formatted CSV file, the erroneous row is deleted.
+ **Address parsing support.** If the `full_addr` tag is used, `libpostal` will be used to parse and split the address into `road`, `house_number`, and so on.
+ **Regex scrubbing.** Easy to handle residual characters or dirty entries, such as whitespace, is cleaned using regular expressions.

### Workflow diagram

OpenTabulate follows a straightforward workflow. Inspect the diagram to see if the design matches your needs.

![Workflow](workflow.png)

