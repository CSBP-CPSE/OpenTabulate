# OpenBusinessRepository
The OpenBusinessRepository (OBuissR) is a listing of businesses records from open data sources. It includes only data or information that was already available to the public on the Internet.

## Installation

...

#### Required dependencies

- `libpostal` library with Python API `pypostal`

## Usage

...

## General program-specific issues
  - Removing the requirement for a header (mainly needed for XML parsing)
  - Require `for` loop in hash table definition to assign empty strings to non-existent fields
  - Handle column merging in MySQL appropriately + replacing old data sets with new ones appropriately
  - Specify a `data_field` key order (might not be needed if using SQL)
  - Have a separate parser that does not handle address parsing.
  - Handle non-existent DPI fields (e.g. "phone" : "Phone", but "Phone" does not exist in data set)
  - For parallelization, the current cheap knock-off is putting `bash` processes in the background -> need a way to determine CPU cores
## Character encoding issues
  - Some data sets are using the legacy encoding ISO 8859-1 (or CP863) instead of UTF-8. The current workaround is to search each data set for 'odd' characters, and if these are found, assume the file is encoded in ISO 8859-1.
  - Some data sets contain the byte order mark (BOM). This breaks the automation process if a field specified by the DPI occurs as the first column, since this first row/column is read. The current workaround is to use a `sed` script to erase the BOM, however, data loss may need to be inspected. 
## Portability issues
  - the data process script is written in Bash
  - libpostal requires administrative access to your machine for installation
