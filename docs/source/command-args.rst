.. _command-args:

======================
Command line arguments
======================

The general usage of OpenTabulate in the command line is of the form::

  opentab [arguments] [SOURCE [SOURCE ...]]

``SOURCE`` here is the path of a :ref:`source file<source-files>`. Multiple source file paths can be included to process in the same command. Remember that the data associated with a source file, i.e. its ``localfile`` tag must placed in the input data directory.

The various command-line arguments are shown in the sections below and are organized by

Flag : Value Type : Possible Values (if applicable)
    *Description...*

^^^^^^^^^^^^^^^^^
Runtime arguments
^^^^^^^^^^^^^^^^^

``-h``, ``--help`` : none
    Print the command-line tool help prompt to standard output.

``--initialize`` : none
    Create the data processing directories used by OpenTabulate in ``$root_directory``.

``-c``, ``--copy-config`` : none
    Copy the example configuration file provided in the package to ``~/.config.opentabulate.conf``.

``-s``, ``--verify-source`` : none
    Validate the given source files without processing their corresponding datasets. Use for checking source file syntax.


^^^^^^^^^^^^^^^^^^^^^^^
Configuration arguments
^^^^^^^^^^^^^^^^^^^^^^^

These options override those configured in the :ref:`configuration file<configuration>` ``~/.config/opentabulate.conf``.

``--add-index BOOL`` : boolean 
    Insert index column to output. This overrides the ``add_index`` configuration option.

``--target-enc ENCODING`` : string : *cp1252*, *utf-8*
    Character encoding of the output. This overrides the ``target_encoding`` configuration option. 

``--output-enc-errors HANDLER`` : string : *strict*, *replace*, *ignore*
    Error handling when re-encoding the input encoding to the target output encoding.
    
    * *strict* throws an error upon a failed encoding and ceases processing
    * *replace* substitutes failed encodings with *?*
    * *ignore* discards failed encodings from the output
    
    This overrides the ``output_encoding_errors`` configuration option.

``--clean-ws BOOL`` : boolean
    Toggle whether or not extraneous whitespace should be cleaned. This overrides the ``clean_whitespace`` configuration option.

``--lowercase BOOL`` : boolean
    Toggle whether or not all output characters should be lowercase. This overrides the ``lowercase_entries`` configuration option.

``-l N``, ``--log-level N`` : integer : *0*, *1*, *2*, *3*
    Set the logger level verbosity. The lower the level, the more verbose. Primarily used for debugging.  This overrides the ``verbosity_level`` configuration option.
