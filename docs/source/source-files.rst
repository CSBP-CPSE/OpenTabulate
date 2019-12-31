.. _source-files:

============
Source files
============

A fundamental component of OpenTabulate and its use to tabulate your data is the *source file*. A source file is a file in JSON format that configures OpenTabulate to process data from a specific dataset. Such information includes the original dataset format, mapping attribute names in the original data to a standardized set of attributes, the name of the dataset stored on the disk, and so on.

We refer to a JSON key-value pair as a *tag*. Some keys may contain a list of key-value pairs, such as ``address_tokens`` containing key-value pairs for ``city``, ``postcode`` and so forth. 

Source files follow a specific format for OpenTabulate to parse. Below is a source file for a business register dataset for Kitchener in Ontario, Canada. ::

  {
      "localfile": "on-kitchener.csv",
      "url": "https://opendata.arcgis.com/datasets/9b9c871eafce491da8a3d926a8a44ef2_0.csv",
      "format": {
          "type": "csv",
	  "delimiter": ",",
	  "quote": "\""
      },
      "database_type": "business",
      "provider": "Municipality of Kitchener",
      "schema": {
          "legal_name": "COMPANY_NAME",
          "business_no": "ID",
	  "address_tokens" : {
	      "street_no": "STREET_NUMBER",
	      "street_name": "STREET_NAME",
	      "unit": "UNIT",
	      "postal_code": "POSTAL_CODE"
	  },
	  "latitude": "Y",
	  "longitude": "X",
      }
  }

The keys within the first pair of curly braces are ``localfile``, ``url``, ``format``, ``database_type``, ``provider`` and ``schema``. Besides ``schema``, tags that occur in this layer are intended for file handling.

* ``localfile``  represents the name of the file (to be) stored locally to the disk.
* ``url`` defines the download link for the dataset
* ``format`` tells OpenTabulate what the dataset's original format is, so as to choose the appropriate algorithms
* ``database_type`` describes which data attribute names will be considered under ``schema``
* ``provider`` defines a column in the tabulation that is auto-filled with the provider name, so distinguishing data is easy if you choose to concatenate it

The ``schema`` tag contains attribute mapping information. OpenTabulate's job is to reformat your data into a tabular format, but you must specify where and which data attributes (from the original dataset) should appear in the tabulated data. Consider ``on-kitchener.csv`` which has a column with the attribute name ``COMPANY_NAME``. Assume by consulting with the data provider, you determine that this column holds legal business names. This best aligns with the key ``legal_name``, which is a standardized column name defined in OpenTabulate. The remaining tags in ``schema`` are determined by a similar methodology with reference to the different keys documented below. 

---------------------------------
How to read the tag documentation
---------------------------------

The documented source file tags are organized to match the structure of the example above. The tag information is structured as

Key : JSON Type : Requirements
    *Description...*

* **Key** : Key name and column name for the tabulated data.
* **JSON Type** : The supported JSON type for the key's value.
* **Requirements** : Specifies if the tag *must* be included and any tag dependencies it has, if any.
* *Description* : A brief description of the what the key represents.


------------------
File handling tags
------------------

The following tags are generally for data file handling and naming. These tags must appear in the first set of curly braces ``{...}`` of the source file.

``localfile`` : string : Required.
    The name of the local data file stored in ``./data/raw/`` to process. If ``url`` is used, the
    downloaded file will be named to value of this key.

``url`` : string : Optional.
    A direct link to the data set as a URL string.

``format`` : object : Required.
    Dataset file format specification.

``database_type`` : string : Required.
    Dataset type to define which ``schema`` tags to use. Currently supports ``business``,
    ``education``, ``hospital``, ``library``, and ``fire_station``.

``encoding`` : string : Optional.
    Dataset character encoding, which can be "utf-8", "cp1252", or "cp437". If not specified, the
    encoding is guessed from these options.

``pre`` : string, list of strings : Optional.
    A path or list of paths to run pre-processing scripts. The relative path starts in the
    configured directory of OpenTabulate.

``post`` : string, list of strings : Optional.
    A path or list of paths to run post-processing scripts. The relative path starts in the
    configured directory of OpenTabulate.

``schema`` : object : Required.
    Description of data schema transcription.

``filter`` : object : Optional.
    Filter rules for choosing which entries to process. ``filter`` contains key which are the
    attributes to filter by. The value of each key is a list of entries (strings) that are
    acceptable to process.

``provider`` : string : Optional.
    Data provider name to auto-fill the column created during tabulation.

    
-----------
Format tags
-----------

The ``format`` tag is a JSON object, specifying data format information so as to tell Opentabulate how to read the raw dataset.


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

The tag ``schema`` is defined as a JSON object, with valid tags described below. They are separated into different categories: general tags, address tags and by database type. References to them are indexed below.

- :ref:`general-tags`
- :ref:`address-tags`
- :ref:`business-tags`
- :ref:`education-tags`
- :ref:`hospital-tags`
- :ref:`library-tags`
- :ref:`fire-station-tags`

.. _general-tags:

^^^^^^^^^^^^
General tags
^^^^^^^^^^^^

These keys can be used for any ``database_type``. Currently, all of them refer to non-address location and contact information.

``address_str`` : string, list of strings : Optional.
    Full address of business (concatenated street name, number, etc.).
    
``address_str_parse`` : string, list of strings : Optional, cannot be used with ``address_tokens``.
    Full address of business. The entries for this key will used with an address parser!
    
``address_tokens`` : object : Optional, cannot be used with ``address_str_parse``.
    Address metadata, such as street number, street name, postal code, etc.
    
``phone`` : string, list of strings : Optional.
    Business phone number.
    
``fax`` : string, list of strings : Optional.
    Business fax number.
    
``email`` : string, list of strings : Optional.
    Business e-mail.
    
``website`` : string, list of strings : Optional.
    Business website.
    
``tollfree`` : string, list of strings : Optional.
    Business toll-free number.
    
``longitude`` : string, list of strings : Optional.
    Longitude coordinate (in degrees) of location.

``latitude`` : string, list of strings : Optional.
    Latitude coordinate (in degrees) of location.
    
.. _address-tags:

^^^^^^^^^^^^^^^^^^
Address schema tag
^^^^^^^^^^^^^^^^^^

The ``address_tokens`` tag (formerly named ``address``) is a JSON object defined inside ``schema``. It cannot be used together with ``address_str_parse``, since the latter invokes an address parser, whereas this tag is reserved for datasets that have already separated the address tokens. *The tags below must be used inside* ``address_tokens``.

``street_no`` : string, list of strings : Optional.
    Street number.
    
``street_name`` : string, list of strings : Optional.
    Street name, type, and direction.
    
``unit`` : string, list of strings : Optional.
    Unit number.

``city`` : string : Optional.
    City name.
    
``province`` : string : Optional.
    Province or territory name; *former tag name:* ``prov/terr``.
    
``country`` : string : Optional.
   Country name.
   
``postal_code`` : string, list of strings : Optional.
   Postal code; *former tag name:* ``postcode``.

.. _business-tags:   
   
^^^^^^^^^^^^^^^^^^^^
Business schema tags
^^^^^^^^^^^^^^^^^^^^

``legal_name`` : string, list of strings : Optional.
    Business (legal) name; *former tag name:* ``bus_name``.
    
``trade_name`` : string, list of strings : Optional.
    Trade name.
    
``business_type`` : string, list of strings : Optional.
    Business type.
    
``business_no`` : string, list of strings : Optional.
    CRA-assigned business number; *former tag name:* ``bus_no``.
    
``licence_type`` : string, list of strings : Optional.
    Business licence type; *former tag name:* ``lic_type``.
    
``licence_no`` : string, list of strings : Optional.
    Business license number; *former tag name:* ``lic_no``.
    
``start_date`` : string, list of strings : Optional.
    Start date of business; *former tag name:* ``bus_start_date``.
   
``closure_date`` : string, list of strings : Optional.
    Closure date of business; *former tag name:* ``bus_cease_date``.
   
``active`` : string, list of strings : Optional.
    Is the business active?
   
``exports`` : string, list of strings : Optional.
    Does this business export?
   
``exp_cn_#`` : string, list of strings : Optional, replace \#  with 1,2 or 3.
    Export country.
    
``naics_#`` : string, list of strings : Optional, replace \# with 2,3,4,5 or 6.
    NAICS \#-digit code.
    
``qc_cae_#`` : string, list of strings : Optional, replace \# with 1 or 2.
    Quebec establishment economic activity code.
    
``qc_cae_desc_#`` : string, list of strings : Optional, replace \# with 1 or 2.
    Quebec establishment economic activity description.
    
.. _education-tags:   

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Education facility schema tags
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``institution_name`` : string, list of strings : Optional.
    Institution (or school) name; *former tag name:* ``ins_name``.
    
``institution_type`` : string, list of strings : Optional.
    Institution type (public, private, etc.); *former tag name:* ``ins_type``.
    
``education_level`` : string, list of strings : Optional.
    Education level (elementary, secondary, post-secondary, etc.); *former tag name:* ``edu_level``.
    
``board_name`` : string, list of strings : Optional.
    School board or district name.
    
``board_code`` : string, list of strings : Optional.
    School board name or district code. (note: usually specific to the data provider)

``range`` : string, list of strings : Optional.
    Education level range (e.g. K-12).
    
``isced010`` : string, list of strings : Optional.
    Boolean value representing the `ISCED`_ level for early childhood education.
    
``isced020`` : string, list of strings : Optional.
    Boolean value representing the `ISCED`_ level for kindergarten.
    
``isced1`` : string, list of strings : Optional.
    Boolean value representing the `ISCED`_ level for elementary.
    
``isced2`` : string, list of strings : Optional.
    Boolean value representing the `ISCED`_ level for junior secondary.
    
``isced3`` : string, list of strings : Optional.
    Boolean value representing the `ISCED`_ level for senior secondary.
    
``isced4+`` : string, list of strings : Optional.
    Boolean value representing the `ISCED`_ level for post-secondary.

.. _ISCED: https://en.wikipedia.org/wiki/International_Standard_Classification_of_Education

.. _hospital-tags:   

^^^^^^^^^^^^^^^^^^^^
Hospital schema tags
^^^^^^^^^^^^^^^^^^^^

``hospital_name`` : string, list of strings : Optional.
    Name of hospital or health centre.
    
``hospital_type`` : string, list of strings : Optional.
    Type of health centre (e.g. Community Hospital, Community Health Centre, etc.)
    
``health_authority`` : string, list of strings : Optional.
    Regional governing health authority.
    
.. _library-tags:
    
^^^^^^^^^^^^^^^^^^^
Library schema tags
^^^^^^^^^^^^^^^^^^^

``library_name`` : string, list of strings : Optional.
    Library name.

``library_type`` : string, list of strings : Optional.
    Library type (depends on the provider, example values are branch or head, or municipal).
    
``library_board`` : string, list of strings : Optional.
    Name of governing library board.
    
.. _fire-station-tags:
    
^^^^^^^^^^^^^^^^^^^^^^^^
Fire station schema tags
^^^^^^^^^^^^^^^^^^^^^^^^

``fire_station_name`` : string, list of strings : Optional.
    Fire station name; *former tag name:* ``fire_stn_name``.
   

-------------------
Additional features
-------------------

Extracting information from data to be tabulated sometimes requires methods beyond simply mapping data attributes, such as regular expression filtering and entry concatenation. To incorporate such methods into OpenTabulate, special keys have been added or specific syntax for key values is taken into account. Below is a complete list of the methods.

* :ref:`concatenating-entries`
* :ref:`manually-inject-or-fill-data`
* :ref:`filtering-with-regular-expressions`
* :ref:`writing-custom-processing-scripts`

  
^^^^^^^^^^^^^^^^^^^^^^^
Debugging syntax errors
^^^^^^^^^^^^^^^^^^^^^^^

OpenTabulate checks the syntax of your source file and will warn you if something is off, but this validation does not cover all situations. Moreover, it cannot make sense of logical errors until either during processing or when you inspect the tabulated output.

.. IMPORTANT: need to update this issue
   
Before posting a question or issue, check this `GitHub issue <https://github.com/CSBP-CPSE/OpenTabulate/issues/12>`_ for clues to erroneous output or functionality.


.. _concatenating-entries:
  
^^^^^^^^^^^^^^^^^^^^^
Concatenating entries
^^^^^^^^^^^^^^^^^^^^^

When writing tags, some keys above support having JSON lists as a value. For example ::

  ...
  "key": ["value1", "value2", "value3"],
  ...

OpenTabulate interprets this as "for each data point to process, concatenate (separating by spaces) the information under the attributes ``value1``, ``value2``, and ``value3`` (in that order) for the data point, and assign it to the standardized attribute ``key`` for further processing.

A common use of this feature is for address parsing. Since address lines (address data that is concatenated into one string) are not supported keys and some datasets will only provide address information in this manner, we still want to tabulate the data. For example, if a dataset has the entry and columns ::

  Business Name, ..., Address Line 1, Address Line 2, Address Line 3, ...
  ...
  "JOHN TITOR TIME MACHINES", ..., "2036 STEINS GATE", "CANADA", "T5T 5R5", ...
  ...

and our source file contains ::

  ...
  "address_str_parse": ["Address Line 1", "Address Line 2", "Address Line 3"],
  ...

then OpenTabulate will process the entry ::

  "2036 STEINS GATE CANADA T5T 5R5"

for ``"JOHN TITOR TIME MACHINES"`` in whatever way ``address_str_parse`` is handled. In this case, ``address_str_parse`` uses an address parser, and will parse the concatenated entry above.


.. _manually-inject-or-fill-data:
  
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Manually inject or fill data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Any string-valued tags that appear anywhere under ``schema`` support what we call the ``force`` value. If a ``force`` value is assigned to a key, OpenTabulate adds and fills the entire output column (corresponding to the key) with that value. A few situations in which this may be helpful are:

* The dataset to process represents a particular city or province, say Winnipeg and Manitoba, but the data does not explicitly have the city and province for any data point. If we want to include the city or province information in the tabulated data, we can add the tags ``"city": "force:Winnipeg"`` and ``"region": "force:Manitoba"`` to the source file. The resulting tabulated data will have columns ``city`` and ``region`` with filled values Winnipeg and Manitoba respectively.
* A dataset on public schools does not describe its own institution type (namely, that the schools are public). Adding ``"institution_type": "force:public"`` to the source file means OpenTabulate will generate a tabulated dataset with an ``institution_type`` column with ``public`` in all of its entries.
* The address parser you're using is more accurate with additional data that may not be explicitly in the dataset. For example, we may have a XML file with a ``<CivicAddress>`` XML tag that contains the street number, name, city, and province, a separate ``<PostalCode>`` XML tag, and no tags for the country. If you know your data resides in Canada, you can write ``"address_str_parse": ["CivicAddress", "force:Canada", "PostalCode"]"`` to inject "Canada" into the entry-concatenated address before running it through the address parser.

The general syntax is ``"key": "force:value"`` for ``schema`` keys that support string values.

**Note:** User-defined content under ``force`` applies *after* :ref:`pre-processing <writing-custom-processing-scripts>` and *before* OpenTabulate's standard processing.


.. _filtering-with-regular-expressions:

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Filtering with regular expressions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Source files support a ``filter`` tag, which is defined in the first set of curly braces ``{...}``.

Each key in ``filter`` is a desired data attribute to filter by. The value of each key is a `Python regular expression <https://docs.python.org/3/library/re.html>`_ which filters values under the attribute. For example, let us say that we have an attribute named ``Place of Interest`` in a dataset and we want to extract park and community center information. These correspond to the values ``Park`` and ``Community Center`` for every place of interest. We can define our filter as ::

  "filter" : { "Places of Interest": "Park|Community Center" }

Note that the filter keys are grouped by a logical ``AND``. For example, if a source file contains ::

  "filter" : {
	  "attribute1" : "regex1",
	  "attribute2" : "regex2",
	  "attribute3" : "regex3"
  }

then each data point is checked if every regular expression returns a match for each attribute-regex pair. Provided all regular expressions return a match, the data point will be marked for processing. Otherwise, the data point is ignored.


.. _writing-custom-processing-scripts:

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Writing custom processing scripts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Note: OpenTabulate currently does not secure or containerize custom scripts. Always check the code from unknown sources before running them!**

The purpose of custom processing scripts is to support automating processing tasks that are not available in OpenTabulate. OpenTabulate handles two types of custom scripts, *pre-processing* and *post-processing*. Pre-processing scripts run strictly before processing in OpenTabulate and post-processing scripts run strictly after processing in OpenTabulate. 

For example, a dataset may only be provided as a Microsoft Excel spreadsheet, which is an unsupported data format in OpenTabulate. In this situtation, writing a pre-processing script that converts the spreadsheet to CSV format is a way to automate its processing by OpenTabulate. 

The requirements for an OpenTabulate custom script is described below. Note that the term "scripts" here refers to executable programs that accept command line arguments. The number of arguments and what they represent depend on if you are writing a pre-processing or post-processing script. 

* For a *pre-processing script*, you must read the first two command line arguments (e.g. ``sys.argv[1]`` and ``sys.argv[2]`` in Python). OpenTabulate enters the path of the raw dataset stored locally into the first argument, and enters the path of the pre-processed output into the second argument.
* For a *post-processing script*, you need to allow for one command line argument (e.g. ``sys.argv[1]`` in Python). OpenTabulate enters the path of the clean dataset into the single argument.

To include the scripts in a source file, use the ``pre`` and ``post`` keys.
