""" Logic for adding/editing/getting entries in tables
"""
from ..core import Band, BoundingBox
from ..products import registry as product_registry


class DatacubeResource(object):
    """ Tiles of products for a given tile specification

    Args:
        db (Database): Database connection
        tilespec (TileSpec): Tile specification for datacube
        storage (str): Storage type from :attr:`tilezilla.stores.STORAGE_TYPES`
    """
    def __init__(self, db, tilespec, storage):
        self.db = db
        self.tilespec = tilespec
        self.storage = storage
        #: int: Tile specification database ID
        self.tilespec_id = self.init_tilespec(tilespec).id

# TileSpec management
    def init_tilespec(self, tilespec):
        return self.db.ensure_tilespec(desc=tilespec.desc,
                                       ul=tilespec.ul,
                                       crs=tilespec.crs_str,
                                       res=tilespec.res,
                                       size=tilespec.size)

# Collection management
    @property
    def collections(self):
        _collections = self.db.search_collections(
            ref_tilespec_id=self.query_tilespec.id)
        if not _collections:
            return None
        return [c.name for c in _collections]

    def get_collection(self, _id):
        return self.db.get_collection(_id, self.storage)

    def get_collection_by_name(self, name):
        return self.db.get_collection_by_name(name, self.storage)

    def search_collections(self, **kwargs):
        return self.db.search_collections(**kwargs)

    def ensure_collection(self, name):
        """ Return Collection ID by name, creating a new one if needed

        Args:
            name (str): Name of collection to add or retrieve

        Returns:
            int: The `id` index of the added collection
        """
        col = self.db.ensure_collection(self.tilespec_id, self.storage, name)
        return col.id

# Tile management
    def get_tile(self, id_):
        _tile = self.db.get_tile(id_)
        if not _tile:
            return None
        return self._make_tile(_tile)

    def get_tile_by_index(self, collection_name, horizontal, vertical):
        _tile = self.db.get_tile_by_index(collection_name, self.storage,
                                          horizontal, vertical)
        if not _tile:
            return None
        return self._make_tile(_tile)

    def ensure_tile(self, collection_name, horizontal, vertical):
        collection = self.ensure_collection(self.tilespec_id,
                                            self.storage,
                                            collection_name)
        bounds = self.tilespec[(vertical, horizontal)].bounds

        tile = self.db.ensure_tile(collection.id, horizontal, vertical, bounds)
        return tile.id

    def _make_tile(self, tile_query):
        return self.tilespec._index_to_tile((tile_query.vertical,
                                             tile_query.horizontal))


class DatasetResource(object):
    """ Individual dataset product observations per collection and tile
    """
    def __init__(self, db, datacube, collection_name):
        self.db = db
        self.datacube = datacube
        self.collection = self.db.ensure_collection(self.datacube.tilespec_id,
                                                    self.datacube.storage,
                                                    collection_name)
        self.collection_id = self.collection.id

    def get_product(self, id_):
        """ Get product by ``id``
        """
        _product = self.db.get_product(id_)
        return self._make_product(_product)

    def get_product_by_name(self, tile_id, name):
        return self._make_product(self.db.get_product_by_name(tile_id, name))

    def get_products_by_name(self, name):
        """ Get product by ``timeseries_id``
        """
        return [self._make_product(prod) for prod in
                self.db.get_products_by_name(name)]

    def ensure_product(self, tile_id, product):
        """ Add a product to index, creating if needed

        Returns:
            int: Database ID of the product added or retrieved
        """
        collection_id = self.db.get_tile(tile_id).ref_collection_id
        return self.db.ensure_product(tile_id, collection_id, product).id

    def _make_product(self, query):
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

    def get_product_bands(self, tile_id, product):
        """ Return list of Bands indexed from a product for a given tile

        Args:
            tile (Tile): Check for products in this tile
            product (BaseProduct): The product to check for

        Returns:
            list[Band]: A list of :class:`Band`s indexed for this product
                and tile
        """
        prod = self.db.get_product_by_name(tile_id, product.timeseries_id)
        return [self._make_band(b) for b in prod.bands]

    def ensure_band(self, product_id, band):
        """ Add a band to index, creating if necessary

        Args:
            product_id (int): ID of product that band belongs to
            band (Band): An observation in some band belonging to a product

        Returns:
            int: Database ID for the band added or retrieved
        """
        return self.db.ensure_band(product_id, band).id

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
