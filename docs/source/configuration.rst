.. _configuration:

=============
Configuration
=============

Configuring OpenTabulate is done by its configuration file, ``~/.config/opentabulate.conf``. An example configuration can be copied to this location using OpenTabulate, detailed in :ref:`basic-usage`.

The syntax of the configuration is simple and straightforward. Lines starting with ``#`` and ``;`` are ignored, which can be used for comments. Empty lines are also ignored. Otherwise, the configuration file should either contain a *section* or a *key-value pair* ::
  
  [section]
  key = value

*The configuration file for OpenTabulate must only have the sections* ``[general]`` *and* ``[labels]``.

The valid key-value pairs for each section are described in the subsections below and organized by

Key : Type : Default Value
    *Description...*

---------------
General section
---------------

The following are valid key-value pairs for the section ``[general]``.

``root_directory`` : path : *None.*
    *(REQUIRED)* The OpenTabulate data processing directory. This tells where OpenTabulate
    can read and write data. After setting this, one should run ``opentab --initialize`` to
    initialize the data processing directories.

``add_index`` : boolean : false
    Add a positive integer index column to the output. The indices start at zero and then
    increment by one for each row added to the output.

``target_encoding`` : string : utf-8
    The output dataset encoding. Currently supports *utf-8* and *cp1252*. For more details
    about encodings, see `here <https://docs.python.org/3/library/codecs.html#standard-encodings>`_.

``output_encoding_errors`` : string : strict
    Error handling for re-encoding the input to the target output encoding. The options are
    *strict*, *replace* and *ignore*. 

    * *strict* throws an error upon a failed encoding and ceases processing
    * *replace* substitutes failed encodings with *?*
    * *ignore* discards failed encodings from the output

``clean_whitespace`` : boolean : false
    A flag for whether or not OpenTabulate should clean extraneous whitespace in the input.

``lowercase_entries`` : boolean : false
    A flag for whether or not OpenTabulate should lowercase all the entries in the input.

``verbosity_level`` : integer : 3
    The default logger level for OpenTabulate to print debugging and error messages. The
    possible values are integers from 0 to 3 (inclusive). The lower the number, the more
    verbose the logging.

--------------
Labels section
--------------

The ``[labels]`` section is required since this is where the output schema is defined. Each key is a *group name* and its value must be a Python tuple of strings. For example, we could have the key-value pairs ::

  metadata = ('name',)
  location = ('longitude', 'latitude')

The group name serves for readability and organizing the output schema. The contents of the Python tuples themselves define the output column names. Generally, these can be named whatever you want. The main exceptions are

- the group names cannot be named after the keys in the ``[general]`` section
- none of the column names can be named ``idx`` or ``provider``
