.. _guide_cli_db:

Database Queries
================

Datasets ingested through Tilezilla are indexed in a database
(see :ref:`guide_configuration_database`). The ``tilez db`` command and
subcommands allows the user to easily query this database without requiring
knowledge of SQL.


Examples
--------

.. include:: ../config_note.rst

1. Find information about the `products` table
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    > tilez db info product
    11:30:36:INFO:*   Information about: <class 'tilezilla.db.sqlite.tables.TableProduct'>
    11:30:36:INFO:==> Number of entries: 6
    11:30:36:INFO:==> Enumerating columns in table: <class 'tilezilla.db.sqlite.tables.TableProduct'>
    11:30:36:INFO:-       COLUMN #   NAME                TYPE
    11:30:36:INFO:-       Col 00     "created"           DATETIME
    11:30:36:INFO:-       Col 01     "updated"           DATETIME
    11:30:36:INFO:-       Col 02     "id"                INTEGER (PRIMARY KEY)
    11:30:36:INFO:-       Col 03     "ref_tile_id"       INTEGER
    11:30:36:INFO:-       Col 04     "timeseries_id"     VARCHAR
    11:30:36:INFO:-       Col 05     "platform"          VARCHAR
    11:30:36:INFO:-       Col 06     "instrument"        VARCHAR
    11:30:36:INFO:-       Col 07     "acquired"          DATETIME
    11:30:36:INFO:-       Col 08     "processed"         DATETIME
    11:30:36:INFO:-       Col 09     "metadata_"         TEXT
    11:30:36:INFO:-       Col 10     "metadata_files_"   TEXT
    11:30:36:INFO:-       HYBRID 00  "n_bands"           ?


2. Find products that weren't fully ingested
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes a product ingest can fail. In order to help recover, we can query
the database to find all bands from products that were partially ingested. In
this example, we know that all products should contain 8 bands.

.. code-block:: bash

    > tilez db search --filter "n_bands != 8" --group_by timeseries_id product
    Searching table "product" where:
    n_bands != 8
    Results:
    <ESPALandsat(timeseries_id=LT50130311995272AAA01, platform/instrument=LANDSAT_5/TM, acquired=1995-09-29T14:34:30.702088+00:00, n_bands=6)>
    <ESPALandsat(timeseries_id=LT50120311995345XXX01, platform/instrument=LANDSAT_5/TM, acquired=1995-12-11T14:27:53.716000+00:00, n_bands=6)>
    <ESPALandsat(timeseries_id=LT50120311996236XXX01, platform/instrument=LANDSAT_5/TM, acquired=1996-08-23T14:43:34.531031+00:00, n_bands=6)>
    <ESPALandsat(timeseries_id=LT50120311999116XXX01, platform/instrument=LANDSAT_5/TM, acquired=1999-04-26T15:05:49.636038+00:00, n_bands=4)>
    <ESPALandsat(timeseries_id=LT50120312011133EDC00, platform/instrument=LANDSAT_5/TM, acquired=2011-05-13T15:16:41.279038+00:00, n_bands=0)>
    <ESPALandsat(timeseries_id=LE70130312012119EDC00, platform/instrument=LANDSAT_7/ETM, acquired=2012-04-28T15:27:40.959821+00:00, n_bands=6)>
