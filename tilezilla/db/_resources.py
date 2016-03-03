""" Logic for adding/editing/getting entries in tables
"""
from tilezilla.tilespec import TileSpec, Tile
from tilezilla.db._util import get_or_add
from tilezilla.db.sqlite.tables import (TableTileSpec, TableCollection,
                                        TableTile, TableProduct, TableBand)


class DatacubeResource(object):
    """ Tiles of products for a given tile specification
    """

    def __init__(self, db, tilespec, storage):
        self._db = db
        self.tilespec = tilespec
        self.storage = storage
        self.init()

# TileSpec management
    def init(self):
        defaults = dict(ul_x=self.tilespec.ul[0],
                        ul_y=self.tilespec.ul[1],
                        crs=self.tilespec.crs_str,
                        res_x=self.tilespec.res[0],
                        res_y=self.tilespec.res[1],
                        size_x=self.tilespec.size[0],
                        size_y=self.tilespec.size[1])
        kwargs = dict(desc=self.tilespec.desc)
        self._tilespec = get_or_add(self._db,
                                    TableTileSpec,
                                    defaults=defaults,
                                    **kwargs)[0]

# Collection management
    @property
    def collections(self):
        _collections = (self._db.session.query(TableCollection)
                        .filter(TableTileSpec.id == self._tilespec.id).all())
        if not _collections:
            return _collections
        return [c.name for c in _collections]

    def get_collection(self, _id):
        return (self._db.session.query(TableCollection)
                .filter_by(id=_id, storage=self.storage).first())

    def get_collection_by_name(self, name):
        return (self._db.session.query(TableCollection)
                .filter_by(name=name, storage=self.storage).first())

    def search_collections(self, **kwargs):
        return self._db.query(TableCollection).filter_by(**kwargs).all()

    def ensure_collection(self, name):
        """ Return Collection ID by name, creating a new one if needed

        Args:
            name (str): Name of collection to add or retrieve
        Returns:
            int: The `id` index of the added collection
        """
        defaults = dict(ref_tilespec_id=self._tilespec.id,
                        storage=self.storage)
        kwargs = dict(name=name)
        collection, added = get_or_add(self._db, TableCollection,
                                       defaults=defaults, **kwargs)
        return collection.id

# Tile management
    def get_tile(self, _id):
        _tile = (self._db.session.query(TableTile)
                 .filter(TableTile.id == _id).first())
        if not _tile:
            return None
        return self._make_tile(_tile)

    def get_tile_by_index(self, horizontal, vertical):
        _tile = self._db.session.query(TableTile).filter_by(
            horizontal=horizontal, vertical=vertical).first()
        if not _tile:
            return None
        return self._make_tile(_tile)

    def ensure_tile(self, collection_name, horizontal, vertical):
        collection_id = self.ensure_collection(collection_name)
        defaults = dict(ref_collection_id=collection_id)
        kwargs = dict(horizontal=horizontal,
                      vertical=vertical,
                      hv='h{}v{}'.format(horizontal, vertical))
        tile, added = get_or_add(self._db, TableTile,
                                 defaults=defaults, **kwargs)
        return tile.id

    def _make_tile(self, tile_query):
        return self.tilespec._index_to_tile((tile_query.vertical,
                                             tile_query.horizontal))


class DatasetResource(object):
    """ Individual dataset product observations per collection and tile
    """
    def __init__(self, db, datacube):
        self._db = db
        self._cube = datacube

    def ensure_product(self, product):
        """ Add a product to index, creating if needed
        """
        # Ensure product's collection exists
        collection_name = product.__class__.__name__
        collection_id = self._cube.ensure_collection(collection_name)

        _product_ids = []
        bbox = product.bounding_box(self._cube.tilespec.crs)
        tiles = self._cube.tilespec.bounds_to_tile(bbox)
        for tile in tiles:
            # Ensure tile in database
            tile_id = self._cube.ensure_tile(collection_name,
                                             tile.horizontal, tile.vertical)
            # Add product
            defaults = dict(platform=product.platform,
                            instrument=product.instrument,
                            processed=product.processed.datetime)
            kwargs = dict(name=product.timeseries_id,
                          ref_collection_id=collection_id,
                          ref_tile_id=tile_id,
                          acquired=product.acquired.datetime)
            _product, added = get_or_add(self._db, TableProduct,
                                         defaults=defaults, **kwargs)
            _product_ids.append(_product.id)
        return _product_ids
