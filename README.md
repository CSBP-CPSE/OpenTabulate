# OpenBusinessRepository
The OpenBusinessRepository (OBuissR) is a listing of businesses records from open data sources. It includes only data or information that was already available to the public on the Internet.

## Installation

...

#### Required dependencies

- `libpostal` library with Python API `pypostal`

## Usage

...

## Program-specific issues
  - Removing the requirement for a header (mainly needed for XML parsing)
  - Require `for` loop in hash table definition to assign empty strings to non-existent fields
  - Handle column merging in MySQL appropriately + replacing old data sets with new ones appropriately
  - Get address parser to handle unit numbers concatenated with street numbers e.g. 212-49 Road Street
  - Specify a `data_field` key order (might not be needed if using SQL)
  - Handle parsing failure in XML parsing
  - Have a separate parser that does not handle address parsing
  - Handle non-existent DPI fields (e.g. "phone" : "Phone", but "Phone" does not exist in data set)

## Portability issues
  - the data process script is written in Bash
  - libpostal requires administrative access to your machine for installation
