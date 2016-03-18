from contextlib import contextmanager

import sqlalchemy as sa

from .sqlite.tables import (Base, TableTileSpec, TableCollection, TableTile,
                            TableProduct, TableBand)


class Database(object):
    """ The database connection
    """

    def __init__(self, engine, session):
        self.engine = engine
        self.session = session

    @classmethod
    def connect(cls, uri, debug=False):
        """ Return a Database for a given URI

        Args:
            URI (str): Resource location
            debug (bool): Turn on sqlalchemy debug echo

        Returns:
            Database
        """
        engine = sa.create_engine(uri, echo=debug)
        Base.metadata.create_all(engine)
        session = sa.orm.sessionmaker(bind=engine)()

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

        return cls.connect(uri=sa.engine.url.URL(**uri_config),
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
        return self.session.query(TableTile).filter_by(desc=name).first()

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
                           ref_tilespec_id=tilespec_id).first())

    def ensure_tile(self, tilespec_id, storage, collection,
                    horizontal, vertical, bounds):
        tile = self.get_tile_by_tile_index(tilespec_id, storage, collection,
                                           horizontal, vertical)
        if not tile:
            with self.scope() as txn:
                tile = TableTile(ref_tilespec_id=tilespec_id,
                                 storage=storage,
                                 collection=collection,
                                 horizontal=horizontal,
                                 vertical=vertical,
                                 bounds=bounds)
                txn.add(tile)
        return tile

# PRODUCTS
    def get_product(self, id_):
        return self.session.query(TableProduct).filter_by(id=id_).first()

    def get_product_by_name(self, tile_id, name):
        return (self.session.query(TableProduct)
                .filter_by(timeseries_id=name,
                           ref_tile_id=tile_id).first())

    def get_products_by_name(self, name):
        return (self.session.query(TableProduct)
                .filter_by(timeseries_id=name).all())

    def ensure_product(self, tile_id, product):
        prod = (self.session.query(TableProduct)
                .filter_by(timeseires_id=product.timeseries_id,
                           ref_tile_id=tile_id))
        if not prod:
            with self.scope() as txn:
                prod = TableProduct(
                    ref_tile_id=tile_id,
                    timeseries_id=product.timeseires_id,
                    platform=product.platform,
                    instrument=product.instrument,
                    acquired=product.acquired,
                    processed=product.processed,
                    metadata_=getattr(product, 'metadata', {}),
                    metadata_files_=getattr(product, 'metadata_files', {})
                )
                txn.add(prod)
        return prod

# BANDS
    def get_band(self, id_):
        return self.session.query(TableBand).filter_by(id=id_).first()

    def get_band_by_name(self, product_id, name):
        return self.session.query(TableBand).filter_by(
            ref_product_id=product_id,
            standard_name=name)

    def ensure_band(self, product_id, band):
        band_ = self.get_band_by_name(product_id, band.standard_name)
        if not band_:
            band_ = TableBand(
                ref_product_id=product_id,
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
        return band_
