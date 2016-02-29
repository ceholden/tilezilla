from tilezilla.db.sqlite.tables import Base, TileSpec, Tile


if __name__ == '__main__':
    from tilezilla import tilespec, products, stores
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
#    engine = create_engine('sqlite:///:memory:', echo=True)
    engine = create_engine('sqlite:///testing.db', echo=True)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    # Create the tile specification
    weld_conus = tilespec.TILESPECS['WELD_CONUS']
    sql_weld_conus = TileSpec.from_class(weld_conus)
    session.add(sql_weld_conus)
    session.commit()

    # Create a product
    prod = products.ESPALandsat('tests/data/LT50120312002300-SC20151009172149_EPSG5070/')

    # Find and add tiles for product
    tiles = weld_conus.bounds_to_tile(prod.bounding_box(weld_conus.crs))
    for tile in tiles:
        sql_tile = Tile(ref_tilespec_id=sql_weld_conus.id,
                        horizontal=tile.horizontal,
                        vertical=tile.vertical,
                        hv='h{}v{}'.format(tile.horizontal, tile.vertical))
        session.add(sql_tile)
    session.commit()
    from IPython.core.debugger import Pdb; Pdb().set_trace()
