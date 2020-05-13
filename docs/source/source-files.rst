.. _source-files:

============
Source files
============

A fundamental component of OpenTabulate and its use to tabulate your data is the *source file*. A source file is a metadata and configuration file in JSON format that directs how OpenTabulate should process a specific dataset. The contents include the input data format, data attribute mapping to the output schema, the filename of the dataset stored on the disk, and so on.

Source files follow a specific format which OpenTabulate parses and validates. Below is an example source file for British Columbia hospital data ::

  {
    "localfile": "bc-hospitals.csv",
    "schema_groups": ["health", "geocoordinates", "address"],
    "source": "https://catalogue.data.gov.bc.ca/dataset/hospitals-in-bc",
    "licence": "https://www2.gov.bc.ca/gov/content/data/open-data/open-government-licence-bc",
    "provider": "Province of British Columbia",
    "encoding": "cp1252",
    "format": {
        "type": "csv",
        "delimiter": ",",
        "quote": "\""
    },
    "schema": {
        "name" : "SV_NAME",
        "health_authority": "RG_NAME",
        "address_str": ["STREET_NUMBER", "CITY", "PROVINCE", "POSTAL_CODE"],
        "geocoordinates" : {
            "longitude": "geo_lon",
            "latitude": "geo_lat"
        }
    }
  }

For brevity, we refer to

- the JSON keys that appear in (the top level of) a pair of closing curly braces as a *layer*
- the JSON key-value pairs as a *tag*

In the above example, the keys found in the first layer are ``localfile``, ``schema_groups``, ``source``, ``licence``, ``provider``, ``encoding``, ``format`` and ``schema``. Besides ``schema``, most of these keys specify metadata and data reading parameters. In more detail:

* ``localfile`` is the filename of a dataset stored in the input directory (to be processed)
* ``schema_groups`` is a list of group names specifying which column names in the output schema are allowed to be used; the group names are defined in ``opentabulate.conf``
* ``source``, ``licence`` and ``provider`` are metadata for organizational purposes; the ``provider`` value is stored in a column in the output format
* ``encoding`` refers to the input data's character encoding
* ``format`` provides parameters to parse the input data
* ``schema`` gives the input data attribute mapping to the output schema

---------------------------------
How to read the tag documentation
---------------------------------

The documented source file tags are organized to match the structure of the example above. The tag information is structured as

Key : JSON Type : Requirements
    *Description...*

* **Key** : Key name.
* **JSON Type** : The supported JSON type for the key's value.
* **Requirements** : Specifies if the tag *must* be included and any dependencies it has, if any.
* *Description* : A brief description of the what the key represents.


-------------------------------
Metadata and configuration tags
-------------------------------

The tags presented refer to the first layer of the source file, i.e. they must appear first set of closing curly braces ``{...}``.

``localfile`` : string : Required.
    The filename of the input data to process stored in ``$root_directory/data/input``.

``schema_groups`` : string, list of strings : Required.
   Groups referring to output column names this source file is allowed to use. The group names are
   specified in the ``[labels]`` section of the configuration file ``opentabulate.conf``.

``format`` : object : Required.
    Input data format specification.

``encoding`` : string : Optional.
    Dataset character encoding, which currently can only be "utf-8" or "cp1252". If not specified,
    the encoding is guessed from these options.

``schema`` : object : Required.
    The mapping of input data attributes to output columns. This describes how the attributes of
    the input dataset should be tabulated. The output column names must appear in the group names
    provided in the ``schema_groups`` tag.

``filter`` : object : Optional.
    Regular expression filter rules for choosing which entries to process. ``filter`` contains
    keys which are the input data attributes to filter on. The value of each key is a regular
    expression string. For more details, see :ref:`filtering-with-regular-expressions`.

``provider`` : string : Optional.
    Data provider name to auto-fill the column *provider* created during tabulation.

``source`` : string : Optional.
    Data source string. Our convention is that this is a URL. This is here purely for organization purposes.

``licence`` : string : Optional.
    Data source licence string. Our convention is that this is a URL. This is here purely for organization purposes.

-----------
Format tags
-----------

The ``format`` tag is a JSON object, specifying input data format information so as to tell Opentabulate how to parse the input data.


``type`` : string : Required.
    The dataset format. Currently supports the values "csv" and "xml".

``header`` : string : Required if ``"type": "xml"``.
    XML tag name identifying a single data point. Each occurence of this tag should contain the
    information referenced in the schema.

``delimiter`` : string : Required if ``"type": "csv"``, must be one character. 
    The delimiting character in the raw CSV dataset.

``quote`` : string : Required if ``"type": "csv"``, must be one character. 
    The quote character in the raw CSV dataset.


-----------
Schema tags
-----------

The tag ``schema`` is defined as a JSON object. It is special in the sense that its contents are largely customized by the user. The formatting of the contents of the ``schema`` tag is important and follows strict rules. First, recall that the output schema is specified in the ``[labels]`` section of the configuration file ``opentabulate.conf``. We might have something like ::

  ...
  [labels]

  geocoordinates = ('longitude', 'latitude')

  facility = ('name',)

The tags in ``schema`` must either be a data attribute mapping tag ::

  # example: "name": "Facility_Name"
  "output_column" : "input_attribute"

or a group tag, with group name key and JSON object value, containing column names from that group ::

  # example:
  # "geocoordinates" : {
  #     "longitude" : "LON",
  #	"latitude" : "LAT"
  # }
  "group_name" : {
      "output_column" : "input_attribute",
      ...
  }

The use of group tags are not necessary and do not change OpenTabulate's output. They are primarily there for readability.

-------------------
Additional features
-------------------

Extracting information from data to be tabulated sometimes requires methods beyond simply mapping data attributes, such as regular expression filtering and entry concatenation. To incorporate such methods into OpenTabulate, special tags have been added or specific syntax for key values is taken into account. Below is a complete list of these features.

* :ref:`concatenating-entries`
* :ref:`manually-inject-or-fill-data`
* :ref:`filtering-with-regular-expressions`

  
.. _concatenating-entries:
  
^^^^^^^^^^^^^^^^^^^^^
Concatenating entries
^^^^^^^^^^^^^^^^^^^^^

When writing ``schema`` tags, all data attribute mapping tags support having JSON lists of strings as a value instead of just a string. This has the effect of concatenating data entries. For example, if we have ::

  "col": ["attr_1", "attr_2", "attr_3"],

OpenTabulate interprets this as "for each entity in the data, concatenate (separating by spaces) the contents of the attributes ``attr_1``, ``attr_2``, and ``attr_3`` (in that order), and then proceed to process this and output to the column ``col``.

.. _manually-inject-or-fill-data:
  
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Manually inject or fill data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Any data attribute tag in ``schema`` that contains the prefix ``force:`` in a string value is interpreted differently. Instead of searching for a data attribute in the input, the substring after the prefix is injected into the data entry for the corresponding output column. It can be used as a single value data filler. For example, if we have ::

  "a" : "force:b"

then OpenTabulate's output will have a column named *a* filled with the character *b*. One can do something more complicated in combination with entry concatenation: ::

  "address" : ["STREET_ADDRESS", "CITY", "force:Canada"]

This has the effect of taking every entity's street address and city name, concatenating them and appending *Canada* at the end of the concatenated string. The string then undergoes further processing and is output to the *address* column.


.. _filtering-with-regular-expressions:

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Filtering with regular expressions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As perhaps seen earlier, source files support a ``filter`` tag in the first layer. ``filter`` contains tags whose values are strings forming `regular expressions <https://docs.python.org/3/library/re.html>`_. Each key is an input data attribute to apply the regular expression to. A data entity is kept if and only if for every key *k*, the regular expression matches the entity's data entry for the attribute *k*. 

-----------------------
Debugging syntax errors
-----------------------

OpenTabulate checks the syntax of your source file and will warn you if something is off, but this validation does not cover all situations. Moreover, it cannot make sense of semantic errors in output until either during processing or when you inspect the output.

Try your best to adhere to the standards and conventions as shown in the documentation. If you discover any bugs or have any further questions, please post an issue in our `GitHub repository <https://github.com/CSBP-CPSE/OpenTabulate/issues>`_.
