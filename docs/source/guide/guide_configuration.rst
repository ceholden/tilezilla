.. _guide_configuration:

=============
Configuration
=============

Tile Specification
------------------

A tile specification describes the positioning, grid layout, and coordinate reference system that ingested imagery will be reprojected, diced, and aligned to match with.

A tile specification is described by four attributes:

* ``crs`` (``str``): The coordinate reference system, given as a Proj4 string or Well-Known-Text.
* ``ul`` (``tuple``): The upper left X and Y coordinates of the tile specification
* ``res`` (``tuple``): The pixel resolution of data in the tile specification
* ``size`` (``tuple``): The number of pixels (columns and rows) in each tile. The total area covered by a tile is a function of the pixel size and the number of pixels per tile.

Tilezilla includes a few "well known specifications" that include:

* WELD_CONUS
    * ``crs``: "EPSG:5070"
    * ``ul``: [-2565600.0, 3314800.0]
    * ``res``: [30, 30]
    * ``size``: [5000, 5000]

.. _guide_configuration_database:

Database
--------

Tilezilla's database backend is written using SQLAlchemy ORM to abstract as much as possible away from the type of database used. Currently, only SQLite has been tested but the structure should be in place to switch to something more complex (e.g., PostgreSQL).

SQLite
~~~~~~
.. todo::
    Describe SQLite configuration

Storage
-------

Tiled data are stored on disk either as a collection of GeoTIFF images or of NetCDF4 files.

Currently, only the GeoTIFF storage format is implemented.

GeoTIFF
~~~~~~~

.. todo::
    Document the GeoTIFF storage format

Example
~~~~~~~

.. todo::
    Provide better configuration file example.

.. literalinclude:: ../../../sandbox/config_schema.yaml
    :language: yaml
