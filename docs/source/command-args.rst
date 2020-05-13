.. _command-args:

======================
Command line arguments
======================

The general usage of OpenTabulate in the command line is of the form::

  opentab [optional arguments] [SOURCE [SOURCE ...]]

``SOURCE`` here is the path of a :ref:`source file<source-files>`. Multiple source file paths can be included to process in the same command. Remember that the data associated with a source file, i.e. its ``localfile`` tag must placed in the input data directory.

The optional command-line arguments are listed in the table below.

+------------+----------------------+-----------------------------------------------------------+
| Short flag | Long flag            | Description                                               |
+============+======================+===========================================================+
| ``-h``     | ``--help``           | Print the command-line tool help prompt to standard       |
|            |                      | output.                                                   |
+------------+----------------------+-----------------------------------------------------------+
| ``-s``     | ``--verify-source``  | Validate the given source files without processing their  |
|            |                      | corresponding datasets. Useful for checking source file   |
|            |                      | syntax.                                                   |
+------------+----------------------+-----------------------------------------------------------+
| ``-l N``   | ``--log-level N``    | Set the logger level verbosity, which is an integer from  |
|            |                      | to 3 (inclusive). The lower the level, the more verbose.  |
|            |                      | Primarily used for debugging.                             |
+------------+----------------------+-----------------------------------------------------------+
| ``-c``     | ``--copy-config``    | Copy the example configuration file provided in the       |
|            |                      | package to ``~/.config/opentabulate``.                    |
+------------+----------------------+-----------------------------------------------------------+
|            | ``--initialize``     | Create the data processing directories used by            |
|            |                      | OpenTabulate in ``$root_directory``.                      |
+------------+----------------------+-----------------------------------------------------------+
