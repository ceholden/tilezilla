.. _guide_cli_ingest:

Ingest
======

The ``tilez ingest`` program slices dataset product images into tiles, writes
these tiled images to disk, and then indexes metadata about these data into a
database for future use.

Usage
-----

.. code-block:: bash

    > tilez ingest --help
    Usage: tilez ingest [OPTIONS] [SOURCES]...

    Options:
      -pe, --parallel-executor [serial|process]
                                Method of parallel execution
      -j, --njob INTEGER        Number of jobs for parallel execution
      --log_dir PATH            Log ingests to this directory (otherwise to
                                stdout)
      --overwrite                     Overwriting existing tiled data
      -h, --help                      Show this message and exit.


.. include:: ../config_note.rst


Examples
--------

.. todo::
    Demo of ``tilez ingest``
