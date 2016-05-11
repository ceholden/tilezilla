.. _guide_spew:


==============================================
Tilezilla Compatibility Command Line Interface
==============================================

Tilezilla stores tiled data in a flexible and extendible manner so that
additional data, including additional bands for the same acquisition, may be
indexed and added. This storage arrangement, however, is not always ideal for
analysis in existing codebases.

The ``tilez spew`` program was written to convert the storage systems used in
Tilezilla (GeoTIFF or NetCDF) into something more familiar. Specifically,
`tilez spew` will create multi-band Virtual Raster dataset (VRT) for each
acquisition containing a collection of bands desired by the user. VRTs should
ease the use of time series of imagery ingested by Tilezilla because the VRTs
bundle multiple bands together.

.. todo::
    Show the ``tilez spew`` usage

Example
-------

To begin, the ``spew`` command needs to know what products in the database to
convert to the VRT format.

.. code-block:: bash

    tilez -v db id --filter "n_bands = 8" --filter "acquired > 2010-01-01" --filter "acquired < 2011-01-01" --group_by timeseries_id product | tilez -v spew VRTs/
