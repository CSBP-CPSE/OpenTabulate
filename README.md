# OpenBusinessRepository
The OpenBusinessRepository (OBuissR) is a listing of businesses records from open data sources. It includes only data or information that was already available to the public on the Internet.

## Installation

...

#### Required dependencies

- `libpostal` library with Python API `pypostal`

## Usage

...

## Issues
  - Removing the requirement for a header (mainly needed for XML parsing)
  - Require `for` loop in hash table definition to assign empty strings to non-existent fields
  - Handle column merging in MySQL appropriately
  - Handle replacing old data sets with new ones appropriately
  - For data processing files, 'address' must be a non-empty list, a string, or not included
  - Get address parser to handle unit numbers concatenated with street numbers e.g. 212-49 Road Street
