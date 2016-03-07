""" SQLite table definitions
"""
import sqlalchemy as sa
import sqlalchemy_utils as sau

Base = sa.ext.declarative.declarative_base()


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
    collections = sa.orm.relationship('TableCollection',
                                      backref='ref_tilespec')


class TableCollection(Base):
    """ Collection of tiled products
    """
    __tablename__ = 'collection'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    ref_tilespec_id = sa.Column(
        sa.ForeignKey(TableTileSpec.id),
        nullable=False)
    name = sa.Column(sa.String, nullable=False)
    storage = sa.Column(sa.String, nullable=False)

    tiles = sa.orm.relationship('TableTile', backref='ref_collection')


class TableTile(Base):
    """ SQL representation of :class:`tilespec.Tile`
    """
    __tablename__ = 'tile'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    ref_collection_id = sa.Column(
        sa.ForeignKey(TableCollection.id),
        nullable=False)
    #: int: Horizontal index of tile in tile specification
    horizontal = sa.Column(sa.Integer)
    #: int: Vertical index of tile in tile specification
    vertical = sa.Column(sa.Integer)
    #: str: Concatenation of horizontal and vertical indices
    hv = sa.Column(sa.String, index=True, unique=True)
    # Reference to product collections stored within this tile
    products = sa.orm.relationship('TableProduct', backref='ref_tile')


class TableProduct(Base):
    """ SQL representation of dataset products
    """
    __tablename__ = 'product'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    ref_collection_id = sa.Column(
        sa.ForeignKey(TableCollection.id),
        nullable=False)
    ref_tile_id = sa.Column(sa.ForeignKey(TableTile.id), nullable=False)
    name = sa.Column(sa.String, index=True, nullable=False)
    platform = sa.Column(sa.String, nullable=False)
    instrument = sa.Column(sa.String, nullable=False)
    acquired = sa.Column(sa.DateTime, nullable=False, index=True)
    processed = sa.Column(sa.DateTime, nullable=False)

    # Reference to individual band observations
    bands = sa.orm.relationship('TableBand', backref='ref_product')


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
