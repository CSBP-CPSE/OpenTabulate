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
  - Perform 'complete address parsing' (concatenate all address related fields and use `address_parse`
  - Handle non-existent DPI fields (e.g. "phone" : "Phone", but "Phone" does not exist in data set)
## Character encoding issues
  - Some data sets are using some kind of legacy encoding (tested ISO 8859-1 and CP863) instead of UTF-8. There has been no success with the ISO encoding, and the Surrey business licenses dataset returns the incorrect characters for both assumed encodings.
## Portability issues
  - the data process script is written in Bash / uses scripts that use bash tools, e.g. `nproc`, `sed`, etc.
  - libpostal requires administrative access to your machine for installation
