""" SQLite table definitions
"""
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class TileSpec(Base):
    """ SQL representation of :class:`tilespec.TileSpec`
    """
    __tablename__ = 'tilespec'
    id = Column(Integer, primary_key=True, autoincrement=True)
    #: str: description of the tile specification
    desc = Column(String, nullable=False)
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
    tiles = relationship('Tile', backref='ref_tilespec')

    @classmethod
    def from_class(cls, obj):
        return cls(
            desc=obj.desc,
            ul_x=obj.ul[0], ul_y=obj.ul[1],
            crs=obj.crs_str,
            res_x=obj.res[0], res_y=obj.res[1],
            size_x=obj.size[0], size_y=obj.size[1]
        )


class Tile(Base):
    """ SQL representation of :class:`tilespec.Tile`
    """
    __tablename__ = 'tile'
    id = Column(Integer, primary_key=True, autoincrement=True)
    #: TileSpec: Tile specification for this tile
    ref_tilespec_id = Column(ForeignKey(TileSpec.id), nullable=False)
    #: int: Horizontal index of tile in tile specification
    horizontal = Column(Integer)
    #: int: Vertical index of tile in tile specification
    vertical = Column(Integer)
    #: str: Concatenation of horizontal and vertical indices
    hv = Column(String, index=True, unique=True)

    # Reference to product collections stored within this tile
    collections = relationship('Collection', backref='ref_tile')
    # products = relationship('Product', backref='ref_tile')


class Collection(Base):
    """ Collection of products
    """
    __tablename__ = 'collection'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ref_tile_id = Column(ForeignKey(Tile.id), nullable=False)
    name = Column(String, nullable=False)

    products = relationship('Product', backref='ref_collection_id')


class Product(Base):
    """ SQL representation of dataset products
    """
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ref_collection_id = Column(ForeignKey(Collection.id), nullable=False)
    name = Column(String, index=True, nullable=False)
    desc = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    instrument = Column(String, nullable=False)
    acquired = Column(DateTime, nullable=False)
    processed = Column(DateTime, nullable=False)

    # Reference to individual band observations


class Variable():
    pass
