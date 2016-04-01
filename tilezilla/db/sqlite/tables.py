""" SQLite table definitions
"""
import sqlalchemy as sa
import sqlalchemy_utils as sau
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TableTileSpec(Base):
    """ SQL representation of :class:`tilespec.TileSpec`
    """
    __tablename__ = 'tilespec'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    #: str: description of the tile specification
    desc = sa.Column(sa.String, nullable=False, unique=True)
    # float: Upper left X/Y coordinates
    ul = sa.Column(sau.ScalarListType(float), nullable=False)
    #: str: Coordinate reference system
    crs = sa.Column(sa.String, nullable=False)
    #: float: Pixel X/Y resolution
    res = sa.Column(sau.ScalarListType(float), nullable=False)
    #: int: Number of rows/columns in each tile
    size = sa.Column(sau.ScalarListType(int), nullable=False)

    # Reference to tiles using this tile specification
    tiles = sa.orm.relationship('TableTile', backref='ref_tilespec')


class TableTile(Base):
    """ SQL representation of :class:`tilespec.Tile`
    """
    __tablename__ = 'tile'
    __table_args__ = (
        # Allow only one unique tile per tilespec per collection/storage method
        sa.UniqueConstraint('horizontal', 'vertical', 'ref_tilespec_id',
                            'storage', 'collection',
                            name='_tilespec_tile_uc'),
    )

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    ref_tilespec_id = sa.Column(sa.ForeignKey(TableTileSpec.id),
                                nullable=False)
    #: str: Name of storage method
    storage = sa.Column(sa.String, index=True, nullable=False)
    #: str: Collection name
    collection = sa.Column(sa.String, index=True, nullable=False)

    #: int: Horizontal index of tile in tile specification
    horizontal = sa.Column(sa.Integer, index=True)
    #: int: Vertical index of tile in tile specification
    vertical = sa.Column(sa.Integer, index=True)
    #: BoundingBox: Bounds of tile in EPSG:4326
    bounds = sa.Column(sau.ScalarListType(float), nullable=False)
    # Reference to product collections stored within this tile
    products = sa.orm.relationship('TableProduct', backref='ref_tile')


class TableProduct(Base):
    """ SQL representation of dataset products
    """
    __tablename__ = 'product'
    __table_args__ = (
        # Allow only one observation (timeseries_id) per tile
        sa.UniqueConstraint('ref_tile_id', 'timeseries_id',
                            name='_tile_store_collection_id_uc'),
    )

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    #: int: Reference to tile containing product
    ref_tile_id = sa.Column(sa.ForeignKey(TableTile.id), nullable=False)

    timeseries_id = sa.Column(sa.String, index=True, nullable=False)
    platform = sa.Column(sa.String, nullable=False)
    instrument = sa.Column(sa.String, nullable=False)
    acquired = sa.Column(sau.ArrowType, nullable=False, index=True)
    processed = sa.Column(sau.ArrowType, nullable=False)

    metadata_ = sa.Column(sau.JSONType, default={})
    metadata_files_ = sa.Column(sau.JSONType, default={})

    # Reference to individual band observations
    bands = sa.orm.relationship('TableBand', backref='ref_product')

    # @sau.aggregated('bands', sa.Column(sa.Integer))
    # def n_bands(self):
    #     return sa.func.count('1')
    @sa.ext.hybrid.hybrid_property
    def n_bands(self):
        return len(self.bands)

    @n_bands.expression
    def n_bands(cls):
        return (sa.select([sa.func.count(TableBand.id)]).
                where(TableBand.ref_product_id == cls.id).
                label('n_bands'))

class TableBand(Base):
    __tablename__ = 'band'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    ref_product_id = sa.Column(
        sa.ForeignKey(TableProduct.id),
        index=True,
        nullable=False)
    path = sa.Column(sa.String, nullable=False)
    bidx = sa.Column(sa.Integer, nullable=False)
    standard_name = sa.Column(sa.String, index=True, nullable=False)
    long_name = sa.Column(sa.String, nullable=False)
    friendly_name = sa.Column(sa.String, nullable=False)
    units = sa.Column(sa.String, nullable=False)
    fill = sa.Column(sa.Float)  # fill can be None
    valid_min = sa.Column(sa.Float, nullable=False)
    valid_max = sa.Column(sa.Float, nullable=False)
    scale_factor = sa.Column(sa.Float)
