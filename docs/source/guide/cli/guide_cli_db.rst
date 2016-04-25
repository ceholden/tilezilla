.. _guide_db:

=========================================
Tilezilla Database Command Line Interface
=========================================

Datasets ingested through Tilezilla are indexed in a database (see :ref:`guide_configuration_database`).

Examples
--------

1. An example
~~~~~~~~~~~~~

2. A more sophisticated example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

3. Find bands belonging to products that weren't fully ingested
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes a product ingest can fail. In order to help recover, we can query the database to find all bands from products that were partially ingested

.. code-block:: bash

    $ tilez -v db search --filter "n_bands != 8" --group_by timeseries_id product
    Searching table "product" where:
    n_bands != 8
    Results:
    <ESPALandsat(timeseries_id=LT50130311995272AAA01, platform/instrument=LANDSAT_5/TM, acquired=1995-09-29T14:34:30.702088+00:00, n_bands=6)>
    <ESPALandsat(timeseries_id=LT50120311995345XXX01, platform/instrument=LANDSAT_5/TM, acquired=1995-12-11T14:27:53.716000+00:00, n_bands=6)>
    <ESPALandsat(timeseries_id=LT50120311996236XXX01, platform/instrument=LANDSAT_5/TM, acquired=1996-08-23T14:43:34.531031+00:00, n_bands=6)>
    <ESPALandsat(timeseries_id=LT50120311999116XXX01, platform/instrument=LANDSAT_5/TM, acquired=1999-04-26T15:05:49.636038+00:00, n_bands=4)>
    <ESPALandsat(timeseries_id=LT50120312011133EDC00, platform/instrument=LANDSAT_5/TM, acquired=2011-05-13T15:16:41.279038+00:00, n_bands=0)>
    <ESPALandsat(timeseries_id=LE70130312012119EDC00, platform/instrument=LANDSAT_7/ETM, acquired=2012-04-28T15:27:40.959821+00:00, n_bands=6)>
