""" SQLite table definitions
"""
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class TableTileSpec(Base):
    """ SQL representation of :class:`tilespec.TileSpec`
    """
    __tablename__ = 'tilespec'
    id = Column(Integer, primary_key=True, autoincrement=True)
    #: str: description of the tile specification
    desc = Column(String, nullable=False, unique=True)
    #: int: Upper left X coordinate
    ul_x = Column(Integer, nullable=False)
    #: int: Upper left Y coordinate
    ul_y = Column(Integer, nullable=False)
    #: str: Coordinate reference system
    crs = Column(String, nullable=False)
    #: float: Pixel X resolution
    res_x = Column(Float, nullable=False)
    # float: Pixel Y resolution
    res_y = Column(Float, nullable=False)
    #: int: Number of columns in each tile
    size_x = Column(Integer, nullable=False)
    #: int: Number of rows in each tile
    size_y = Column(Integer, nullable=False)

    # Reference to tiles using this tile specification
    collections = relationship('TableCollection', backref='ref_tilespec')

    @classmethod
    def from_class(cls, obj):
        return cls(
            desc=obj.desc,
            ul_x=obj.ul[0], ul_y=obj.ul[1],
            crs=obj.crs_str,
            res_x=obj.res[0], res_y=obj.res[1],
            size_x=obj.size[0], size_y=obj.size[1]
        )


class TableCollection(Base):
    """ Collection of tiled products
    """
    __tablename__ = 'collection'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ref_tilespec_id = Column(ForeignKey(TableTileSpec.id), nullable=False)
    name = Column(String, nullable=False)
    storage = Column(String, nullable=False)

    tiles = relationship('TableTile', backref='ref_collection')


class TableTile(Base):
    """ SQL representation of :class:`tilespec.Tile`
    """
    __tablename__ = 'tile'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ref_collection_id = Column(ForeignKey(TableCollection.id), nullable=False)
    #: int: Horizontal index of tile in tile specification
    horizontal = Column(Integer)
    #: int: Vertical index of tile in tile specification
    vertical = Column(Integer)
    #: str: Concatenation of horizontal and vertical indices
    hv = Column(String, index=True, unique=True)
    # Reference to product collections stored within this tile
    products = relationship('TableProduct', backref='ref_tile')


class TableProduct(Base):
    """ SQL representation of dataset products
    """
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ref_collection_id = Column(ForeignKey(TableCollection.id),
                               nullable=False)
    ref_tile_id = Column(ForeignKey(TableTile.id), nullable=False)
    name = Column(String, index=True, nullable=False)
    platform = Column(String, nullable=False)
    instrument = Column(String, nullable=False)
    acquired = Column(DateTime, nullable=False, index=True)
    processed = Column(DateTime, nullable=False)

    # Reference to individual band observations
    bands = relationship('TableBand', backref='ref_product')


class TableBand(Base):
    __tablename__ = 'band'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ref_product_id = Column(ForeignKey(TableProduct.id),
                            index=True, nullable=False)
    path = Column(String, nullable=False)
    bidx = Column(Integer, nullable=False)
    standard_name = Column(String, index=True, nullable=False)
    long_name = Column(String, nullable=False)
    friendly_name = Column(String, nullable=False)
    units = Column(String, nullable=False)
    fill = Column(Float)  # fill can be None
    valid_min = Column(Float, nullable=False)
    valid_max = Column(Float, nullable=False)
    scale_factor = Column(Float)
