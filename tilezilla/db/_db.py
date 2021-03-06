from contextlib import contextmanager

import sqlalchemy as sa

from ._tables import (Base, TableTileSpec, TableTile,
                      TableProduct, TableBand)


class Database(object):
    """ The database connection
    """

    def __init__(self, engine, session):
        self.engine = engine
        self.session = session

    @classmethod
    def connect(cls, uri, connect_args=None, debug=False):
        """ Return a Database for a given URI

        Args:
            URI (str): Resource location
            connect_args (dict): Optional connection arguments
            debug (bool): Turn on sqlalchemy debug echo

        Returns:
            Database
        """
        engine = sa.create_engine(uri, echo=debug, connect_args=connect_args)
        Base.metadata.create_all(engine)
        session = sa.orm.scoped_session(sa.orm.sessionmaker(bind=engine))

        return cls(engine, session)

    @classmethod
    def from_config(cls, config=None):
        # http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls
        config = config or {}
        uri_config = {
            'drivername': config.get('drivername'),
            'database': config.get('database'),
            'username': config.get('username', '') or None,
            'password': config.get('password', '') or None,
            'host': config.get('host', '') or None,
            'port': config.get('port', '') or None
        }
        connect_args = {}
        if config.get('drivername') == 'sqlite':
            connect_args['check_same_thread'] = False

        return cls.connect(uri=sa.engine.url.URL(**uri_config),
                           connect_args=connect_args,
                           debug=config.get('debug', False))

    def scope(self):
        """ Session as a context manager

        Intended to be used as follows:

        ..code-block:: python

            with db.scope() as scope:
                # do stuff

        """
        @contextmanager
        def _scope():
            try:
                yield self.session
                self.session.commit()
            except:
                self.session.rollback()
                raise

        return _scope()

# TILE SPECIFICATIONS
    def get_tilespec(self, id_):
        return self.session.query(TableTileSpec).filter_by(id=id_).first()

    def get_tilespec_by_name(self, name):
        return self.session.query(TableTileSpec).filter_by(desc=name).first()

    def ensure_tilespec(self, desc, ul, crs, res, size):
        """ Get or add a TileSpec to the database
        """
        spec = self.get_tilespec_by_name(desc)
        if not spec:
            with self.scope() as txn:
                spec = TableTileSpec(desc=desc,
                                     ul=ul,
                                     crs=crs,
                                     res=res,
                                     size=size)
                txn.add(spec)
        return spec

# TILES
    def get_tile(self, id_):
        return self.session.query(TableTile).filter_by(id=id_).first()

    def get_tile_by_tile_index(self, tilespec_id, storage, collection,
                               horizontal, vertical):
        return (self.session.query(TableTile)
                .filter_by(horizontal=horizontal,
                           vertical=vertical,
                           tilespec_id=tilespec_id).first())

    def create_tile(self, tilespec_id, storage, collection,
                    horizontal, vertical, bounds):
        return TableTile(tilespec_id=tilespec_id,
                         storage=storage,
                         collection=collection,
                         horizontal=horizontal,
                         vertical=vertical,
                         bounds=bounds)

    def ensure_tile(self, tilespec_id, storage, collection,
                    horizontal, vertical, bounds):
        tile = self.get_tile_by_tile_index(
            tilespec_id, storage, collection, horizontal, vertical)
        if not tile:
            tile = self.create_tile(
                tilespec_id=tilespec_id,
                storage=storage,
                collection=collection,
                horizontal=horizontal,
                vertical=vertical,
                bounds=bounds)
            try:
                with self.scope() as txn:
                    txn.add(tile)
            except sa.exc.IntegrityError:
                tile = self.get_tile_by_tile_index(
                    tilespec_id, storage, collection, horizontal, vertical)
                if not tile:
                    raise
        return tile

# PRODUCTS
    def get_product(self, id_):
        return self.session.query(TableProduct).filter_by(id=id_).first()

    def get_product_by_name(self, tile_id, name):
        return (self.session.query(TableProduct)
                .filter_by(timeseries_id=name,
                           tile_id=tile_id).first())

    def get_products_by_name(self, name):
        return (self.session.query(TableProduct)
                .filter_by(timeseries_id=name).all())

    def create_product(self, product):
        return TableProduct(
            timeseries_id=product.timeseries_id,
            platform=product.platform,
            instrument=product.instrument,
            acquired=product.acquired,
            processed=product.processed,
            metadata_=getattr(product, 'metadata', {}),
            metadata_files_=getattr(product, 'metadata_files', {})
        )

    def ensure_product(self, tile_id, product):
        product_ = self.get_product_by_name(tile_id, product.timeseries_id)
        if not product_:
            with self.scope() as txn:
                product_ = self.create_product(product)
                product.tile_id = tile_id
                txn.add(product_)
        return product_

    def update_product(self, tile_id, product):
        product_ = self.get_product_by_name(tile_id, product.timeseries_id)
        new_product = self.create_product(product)
        new_product.tile_id = tile_id
        with self.scope() as txn:
            if product_:
                new_product.id = product_.id
                txn.merge(new_product)
            else:
                txn.add(new_product)
        return new_product

# BANDS
    def get_band(self, id_):
        return self.session.query(TableBand).filter_by(id=id_).first()

    def get_band_by_name(self, product_id, name):
        return self.session.query(TableBand).filter_by(
            product_id=product_id,
            standard_name=name).first()

    def ensure_band(self, product_id, band):
        band_ = self.get_band_by_name(product_id, band.standard_name)
        if not band_:
            with self.scope() as txn:
                band_ = self._create_band(band)
                band_.product_id = product_id
                txn.add(band_)
        return band_

    def update_band(self, product_id, band):
        band_ = self.get_band_by_name(product_id, band.standard_name)
        new_band = self.create_band(band)
        new_band.product_id = product_id
        with self.scope() as txn:
            if band_:
                new_band.id = band_.id
                txn.merge(new_band)
            else:
                txn.add(new_band)
        return new_band

    def create_band(self, band):
        """ :class:`Band` to :class:`TableBand` without a `product_id`
        """
        return TableBand(
            standard_name=band.standard_name,
            path=band.path,
            bidx=band.bidx,
            long_name=band.long_name,
            friendly_name=band.friendly_name,
            units=band.units,
            fill=band.fill,
            valid_min=band.valid_min,
            valid_max=band.valid_max,
            scale_factor=band.scale_factor
        )
