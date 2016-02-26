""" SQLite table definitions
"""
from sqlalchemy import Column, ForeignKey, Integer, Float, String
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
    tilespec_ref = Column(ForeignKey(TileSpec.id), nullable=False)
    #: int: Horizontal index of tile in tile specification
    horizontal = Column(Integer, index=True)
    #: int: Vertical index of tile in tile specification
    vertical = Column(Integer, index=True)

    # Reference to products stored within this tile
    products = relationship('Product', backref='ref_tile')


class Product(Base):
    """ SQL representation of dataset products
    """
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True, autoincrement=True)
    tile_id = Column(ForeignKey(Tile.id), nullable=False)
    name = Column(String, index=True)
    desc = Column(String)

    # Reference to individual band observations


if __name__ == '__main__':
    from tilezilla import tilespec, products, stores
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine('sqlite:///:memory:', echo=True)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    weld_conus = tilespec.TILESPECS['WELD_CONUS']
    ts = TileSpec.from_class(weld_conus)
    prod = products.ESPALandsat('tests/data/LT50120312002300-SC20151009172149_EPGS5070/')
    
    from IPython.core.debugger import Pdb; Pdb().set_trace()
