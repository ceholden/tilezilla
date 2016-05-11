.. _guide_configuration:

=============
Configuration
=============

Tile Specification
------------------

A tile specification describes the positioning, grid layout, and coordinate
reference system that ingested imagery will be reprojected, diced, and aligned
to match with.

A tile specification is described by four attributes:

* ``crs`` (``str``): The coordinate reference system, given as a Proj4 string
  or Well-Known-Text.
* ``ul`` (``tuple``): The upper left X and Y coordinates of the tile
  specification
* ``res`` (``tuple``): The pixel resolution of data in the tile specification
* ``size`` (``tuple``): The number of pixels (columns and rows) in each tile.
  The total area covered by a tile is a function of the pixel size and the
  number of pixels per tile.

Tilezilla includes a few "well known specifications" that include:

* WELD_CONUS
    * ``crs``: "EPSG:5070"
    * ``ul``: [-2565600.0, 3314800.0]
    * ``res``: [30, 30]
    * ``size``: [5000, 5000]

.. _guide_configuration_database:

Database
--------

Tilezilla's database backend is written using SQLAlchemy ORM to abstract as
much as possible away from the type of database used. Currently, only SQLite
has been tested but the structure should be in place to switch to something
more complex (e.g., PostgreSQL).

SQLite
~~~~~~
.. todo::
    Describe SQLite configuration

Storage
-------

Tiled data are stored on disk either as a collection of GeoTIFF images or
NetCDF4 files.

Currently, only the GeoTIFF storage format is implemented.

GeoTIFF
~~~~~~~

.. todo::
    Document the GeoTIFF storage format


Products
--------

.. todo::
    Write about existing products (ESPALandsat) and how one can write YAML
    file to describe arbitrary products for ingest

Example
-------

The following example configuration file describes the configuration needed
to ingest Landsat data processed to surface reflectance through the
`ESPA <espa.cr.usgs.gov>`_ system into a tiling scheme that has the same
parameters as the `Web Enabled Landsat Data (WELD) <weld.cr.usgs.gov>`_
tiled data product.

The ``include_filter`` option in the ``products`` section
limits the ingest to only include surface reflectance, brightness temperature,
and CFmask bands. Any reprojection necessary for this ingest will be done using
nearest neighbor resampling.

.. literalinclude:: ../../../sandbox/demo_ingest.yaml
    :language: yaml
