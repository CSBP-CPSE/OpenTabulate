.. _basic-usage:

===========
Basic usage
===========

This section details a comprehensive example to illustrate usage of OpenTabulate.

For example's sake, let's say you are interested in tabulating hospital location data, where the data of interest is latitude-longitude coordinates, hospital name and regional health authority. The data collected generally does not share the same schema (data attributes) but is structured enough to extract this information. How do we go about using OpenTabulate to achieve our goal of organizing and tabulating this data?

First, an output schema is formalized. Say that we want to output CSVs to have the column names ::

  name, health_authority, longitude, latitude

We must specify this in the OpenTabulate configuration, which will be made use of in a *source file*. Source files will be discussed in a bit, for now simply take each of them to be metadata and configuration for a specific dataset.

The OpenTabulate configuration file is ``~/.config/opentabulate.conf``, which should have be in place after following the installation instructions. Its structure is simple, consisting of sections and key-value pairs. ::

  [section]
  key = value
  key = value
  ...

  [section]
  ...

As provided, there should be exactly two sections, ``[general]`` and ``[labels]``. The *labels* section is where the output schema is specified. The key is the *group name*, which only serves for readability. The value is a Python tuple of strings. Based on the desired output schema, we edit the configuration to be ::

  [labels]
  hospital = ('name', 'health_authority')
  location = ('longitude', 'latitude')

The next, and probably most involved step, is to write a *source file* for each dataset to process. Let's say we have two datasets ``hospitals-bc.csv`` ::

  HOSPITAL_NAME,RG_NAME,X,Y
  Burnaby Hospital,Fraser Health Authority,-123.016837,49.248776
  Fort St. John Hospital,Northern Health Authority,-120.817122,56.256892
  "UBC Hospital, Purdy Pavilion",Vancouver Coastal Health,-123.245945,49.263388

and ``hospitals-ab.xml`` ::

  <?xml version="1.0" encoding="UTF-8"?>
  <HospitalData>
    <Hospital id="1">
    <Name>Canmore General Hospital</Name>
    <City>Calgary</City>
    <Geocoordinates>
      <Longitude>-115.35172</Longitude>
      <Latitude>51.092455</Latitude>
    </Geocoordinates>
    </Hospital>
    <Hospital id="2">
    <Name>Alberta Children's Hospital</Name>
    <City>Calgary</City>
    <Geocoordinates>
      <Longitude></Longitude>
      <Latitude></Latitude>
    </Geocoordinates>
    </Hospital>
  </HospitalData>
  
First we want to place this data where OpenTabulate will read them. They will be located in the directory::

  $root_directory/data/input

where ``$root_directory`` refers to the path in the ``root_directory`` variable in the configuration file. In the example provided in the installation section, ``$root_directory`` is ``/home/bob/opentabulate``.

To direct OpenTabulate on how to tabulate this data into our schema, we need to write a source file for each dataset. A source file is written in JSON format, and is usually very brief. Minimal examples for our example datasets are shown below.

For ``hospitals-bc.csv``, our source file is named ``src-hospitals-bc.json`` and contains ::

  {
    "localfile": "hospitals-bc.csv",
    "schema_groups": ["hospital", "location"],
    "format": {
        "type": "csv",
        "delimiter": ",",
        "quote": "\""
    },
    "schema": {
        "hospital" : {
	    "name" : "HOSPITAL_NAME",
            "health_authority": "RG_NAME"
	},
        "location" : {
            "longitude": "X",
            "latitude": "Y"
        }
    }
  }


and for ``hospitals-ab.xml`` we have ``src-hospitals-ab.json`` which contains ::

  {
    "localfile": "hospitals-ab.xml",
    "schema_groups": ["hospital", "location"],
    "format": {
        "type": "xml",
        "header": "Hospital"
    },
    "schema": {
        "name": "Name",
        "location" : {
            "longitude": "X",
            "latitude": "Y"
	}
    }
  }

Each JSON key has a specific meaning in the source file:

- ``localfile`` specifies the filename of the dataset in the input directory
- ``schema_groups`` refer to which group names (those configured in the ``[labels]`` section of ``opentabulate.conf``) are allowed to be used
- ``format`` detail the input file format parameters
- ``schema`` describes the schema mapping that the tabulation will use

In particular, the contents ``schema``of the form ``"output_column" : "input_attribute"`` tell OpenTabulate how to precisely map the input data to the output. The use of group names in ``schema`` are for organizational purposes.

Where should source files be stored? They can be stored anywhere, but by our convention we organize them here::

  $root_directory/sources

Now we are ready to process! Simply run ::

  $ opentab src-hospitals-ab.json src-hospitals-bc.json

Replace the source file names with paths to them as needed. The resulting output files should be ::

  $root_directory/data/output/hospitals-bc.csv
  $root_directory/data/output/hospitals-ab.csv

with output (up to permutation of the columns) ::

  name,health_authority,longitude,latitude
  Burnaby Hospital,Fraser Health Authority,-123.016837,49.248776
  Fort St. John Hospital,Northern Health Authority,-120.817122,56.256892
  "UBC Hospital, Purdy Pavilion",Vancouver Coastal Health,-123.245945,49.263388

and ::

  name,health_authority,longitude,latitude
  Canmore General Hospital,,-115.35172,51.092455
  Alberta Children's Hospital,,,

respectively.
