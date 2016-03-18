""" Database for ``tilezilla``

This submodule assists with access to the database that indexes products
ingested by `tilezilla`. The chief way of accessing the database is via
the :class:`Database`, :class:`DatacubeResource`, and :class:`DatasetResource`.

The "resources" are designed to be a higher level access to
the database. As such, :class:`DatacubeResource` and :class:`DatasetResource`
both return instances of the object type (a tile specification, a tile, a
product, a band) requested while :class:`Database` will return a SqlAlchemy ORM
object instance retrieved from the database.

The :class:`DatacubeResource` handles tile specifications and tiles while the
:class:`DatasetResource` deals with products and bands.

TODO:
* Searches
    * Search using `filter_by` by combining keyword arguments for each database
      level (Tile, Product, Band) and dictionaries passed to these
      keyword arguments
    * Tie this search into click CLI (multiple key=value flags)
* Database info request
    * Get fields
    * Tie field enumeration to click CLI
    * Some kind of field -> click option generator?
    * E.g., ``tilez db info tile --horizontal=<int>``
* Summary statistics about a database tile, collection, etc.
    * http://sqlalchemy-utils.readthedocs.org/en/latest/aggregates.html
"""
from .sqlite.tables import (TableTileSpec, TableTile, TableProduct, TableBand)
from ._db import Database
from ._resources import DatacubeResource, DatasetResource

TABLES = {
    'tilespec': TableTileSpec,
    'tile': TableTile,
    'product': TableProduct,
    'band': TableBand
}

__all__ = [
    'Database',
    'DatacubeResource',
    'DatasetResource'
]
