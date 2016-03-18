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

# Tile management
    def get_tile(self, id_):
        _tile = self.db.get_tile(id_)
        if not _tile:
            return None
        return self._make_tile(_tile)

    def get_tile_by_tile_index(self, collection, horizontal, vertical):
        _tile = self.db.get_tile_by_tile_index(
            self.tilespec_id, collection, self.storage,
            horizontal, vertical)
        if not _tile:
            return None
        return self._make_tile(_tile)

    def ensure_tile(self, collection, horizontal, vertical):
        bounds = self.tilespec[(vertical, horizontal)].bounds

        tile = self.db.ensure_tile(self.tilespec_id, self.storage,
                                   collection, horizontal, vertical, bounds)
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
        self.collection = collection_name

    def get_product(self, id_):
        """ Get product by ``id``
        """
        _product = self.db.get_product(id_)
        if not _product:
            return None
        return self._make_product(_product)

    def get_product_by_name(self, tile_id, name):
        """ Get product by name within a tile
        """
        _product = self.db.get_product_by_name(tile_id, name)
        if not _product:
            return None
        return self._make_product(_product)

    def get_products_by_name(self, name):
        """ Get all products matching ``timeseries_id``, regardless of tile
        """
        return [self._make_product(prod) for prod in
                self.db.get_products_by_name(name)]

    def get_products_by_tile(self, tile_id):
        """ Get all products within a tile
        """
        return [self._make_product(_prod) for _prod in
                self.datacube.get_tile(tile_id).products]

    def ensure_product(self, tile_id, product):
        """ Add a product to index, creating if needed

        Returns:
            int: Database ID of the product added or retrieved
        """
        return self.db.ensure_product(tile_id, product).id

    def _make_product(self, query):
        product_class = product_registry.products[query.ref_tile.collection]
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
            tile_id (int): Check for products in this tile
            product (BaseProduct): The product to check for

        Returns:
            list[Band]: A list of :class:`Band`s indexed for this product
                and tile
        """
        prod = self.db.get_product_by_name(tile_id, product.timeseries_id)
        if not prod:
            return None
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

    def update_band(self, product_id, band):
        """ Add a new band, updating existing band if necessary

        Args:
            product_id (int): ID of product that band belongs to
            band (Band): An observation in some band belonging to a product

        Returns:
            int: Database ID for band added or updated
        """
        return self.db.update_band(product_id, band).id

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
