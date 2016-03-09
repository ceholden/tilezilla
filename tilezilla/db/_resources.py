""" Logic for adding/editing/getting entries in tables
"""
from ._util import get_or_add
from .sqlite.tables import (TableTileSpec, TableCollection,
                            TableTile, TableProduct, TableBand)
from ..tilespec import TileSpec, Tile
from ..geoutils import reproject_bounds
from ..core import Band, BoundingBox
from ..products import registry as product_registry


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
        defaults = dict(ul=self.tilespec.ul,
                        crs=self.tilespec.crs_str,
                        res=self.tilespec.res,
                        size=self.tilespec.size)
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
        defaults = dict(
            ref_collection_id=collection_id,
            bounds=self.tilespec[(vertical, horizontal)].bounds
        )
        kwargs = dict(
            horizontal=horizontal,
            vertical=vertical,
            hv='h{}v{}'.format(horizontal, vertical),

        )
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

    def get_product(self, id_):
        """ Get product by ``id``
        """
        # TODO: call "make" to get an object
        _product = self._db.session.query(TableProduct).filter_by(id=id_).first()
        return self._make_product(_product)

    def ensure_product(self, tile_id, product):
        """ Add a product to index, creating if needed

        Returns:
            list[int]: A list of IDs for each product added to a tile
        """
        collection_id = (self._db.session.query(TableTile)
                         .filter_by(id=tile_id).first().ref_collection_id)
        # Add product
        defaults = dict(
            platform=product.platform,
            instrument=product.instrument,
            processed=product.processed.datetime,
            metadata_=getattr(product, 'metadata', {}),
            metadata_files_=getattr(product, 'metadata_files', {})
        )
        kwargs = dict(
            timeseries_id=product.timeseries_id,
            ref_collection_id=collection_id,
            ref_tile_id=tile_id,
            acquired=product.acquired.datetime
        )
        _product, added = get_or_add(self._db, TableProduct,
                                     defaults=defaults, **kwargs)
        return _product.id

    def _make_product(self, query):
        # TODO: turn query into Product class instance with bands
        product_class = product_registry.products[query.ref_collection.name]
        bands = [self._make_band(b) for b in query.bands]

        return product_class(
            timeseries_id=query.timeseries_id,
            acquired=query.acquired,
            processed=query.processed,
            platform=query.platform,
            instrument=query.instrument,
            bounds=BoundingBox(*query.ref_tile.bounds),
            bands=bands
        )

    def ensure_band(self, product_id, band):
        """ Add a band to index, creating if necessary

        Args:
            product_id (int): ID of product that band belongs to
            band (Band): An observation in some band belonging to a product

        Returns:
            list[int]: A list of IDs for each band added to tile
        """
        kwargs = dict(ref_product_id=product_id,
                      standard_name=band.standard_name)
        defaults = dict(path=band.path,
                        bidx=band.bidx,
                        long_name=band.long_name,
                        friendly_name=band.friendly_name,
                        units=band.units,
                        fill=band.fill,
                        valid_min=band.valid_min,
                        valid_max=band.valid_max,
                        scale_factor=band.scale_factor)
        _band, added = get_or_add(self._db, TableBand,
                                  defaults=defaults, **kwargs)
        return _band.id

    def _make_band(self, query):
        return Band(
            path=query.path,
            bidx=query.bidx,
            standard_name=query.standard_name,
            long_name=query.long_name,
            friendly_name=query.friendly_name,
            units=query.units,
            fill=query.fill,
            valid_min=query.valid_min,
            valid_max=query.valid_max,
            scale_factor=query.scale_factor
        )
