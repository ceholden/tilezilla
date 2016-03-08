""" Database for ``tilezilla``

TODO:
* Searches
    * Search using `filter_by` by combining keyword arguments for each database
      level (Collection, Tile, Product, Band) and dictionaries passed to these
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
from .sqlite.tables import (TableTileSpec, TableCollection,
                                TableTile, TableProduct, TableBand)

TABLES = {
    'tilespec': TableTileSpec,
    'collection': TableCollection,
    'tile': TableTile,
    'product': TableProduct,
    'band': TableBand
}
