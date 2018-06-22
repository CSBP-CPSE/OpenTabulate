# OpenBusinessRepository
The OpenBusinessRepository (OBuissR) is a listing of businesses records from open data sources. It includes only data or information that was already available to the public on the Internet.

## Installation

...

#### Required dependencies

- `libpostal` library with Python API `pypostal`

## Usage

...

## General program-specific issues and to-do list
  - Require `for` loop in hash table definition to assign empty strings to non-existent fields
  - Handle column merging in MySQL appropriately + replacing old data sets with new ones appropriately
  - Have a separate parser that does not handle address parsing.
  - Perform 'complete address parsing' (concatenate all address related fields and use `address_parse`
  - For fields NOT specified by the DPI, append them anyway with blank fields
## Portability issues
  - many tools are currently written in Bash, mainly for text manipulation and interactive processing 
  - libpostal requires administrative access to your machine for installation
