from tilezilla.db._db import Database
from tilezilla.db._util import get_or_add
from tilezilla.db._resources import DatacubeResource
from tilezilla.db.sqlite.tables import (Base, TileSpec, Collection,
                                        Tile, Product, Band)



#


if __name__ == '__main__':
    from tilezilla import tilespec, products, stores, _util
    # engine = create_engine('sqlite:///:memory:', echo=True)
    # engine = create_engine('sqlite:///testing.db', echo=True)
    # Base.metadata.create_all(engine)
    # session = sessionmaker(bind=engine)()

    # Get the database
    db = Database.from_config()
    # Create the tile specification
    weld_conus = tilespec.TILESPECS['WELD_CONUS']
    # Create a product
    prod = products.ESPALandsat('tests/data/LT50120312002300-SC20151009172149_EPSG5070/')
    # Create datacube resource
    datacube = DatacubeResource(db, weld_conus)
    # Add / get collection
    collection_name = prod.__class__.__name__
    datacube.add_collection(collection_name)
    from IPython.core.debugger import Pdb; Pdb().set_trace()

    # Create/get collection for product
    include_pattern = {
        'long_name': ('.*surface reflectance.*',
                      '.*brightness temperature.*',
                      '^cfmask_band$')
    }
    desired_bands = _util.include_bands(prod.bands,
                                        include_pattern, regex=True)

    # Find and add tiles for product
    tiles = list(weld_conus.bounds_to_tile(prod.bounding_box(weld_conus.crs)))
    for tile in tiles:
        # TODO: wrap up somewhere --> TileResource
        sql_tile = Tile(ref_collection_id=sql_collection.id,
                        horizontal=tile.horizontal,
                        vertical=tile.vertical,
                        hv='h{}v{}'.format(tile.horizontal, tile.vertical))
        session.add(sql_tile)
        session.commit()

        # TODO: wrap up somewhere --> ProductResource
        product_attrs = dict(
            ref_collection_id=sql_collection.id,
            ref_tile_id=sql_tile.id,
            name=prod.timeseries_id,
            platform=prod.platform,
            instrument=prod.instrument,
            acquired=prod.acquisition_datetime.datetime,
            processed=prod.processed_datetime.datetime
        )
        sql_product, created = get_or_add(session, Product, **product_attrs)
        if created:
            session.commit()

        for band in desired_bands:
            # TODO: some sort of product.add_band
            band_attrs = dict(
                ref_product_id=sql_product.id,
                path=band.path,
                bidx=band.bidx,
                standard_name=band.standard_name,
                long_name=band.long_name,
                friendly_name=band.friendly_name,
                units=band.units,
                fill=band.fill,
                valid_min=band.valid_min,
                valid_max=band.valid_max,
                scale_factor=band.scale_factor
            )
            sql_band, band_created = get_or_add(session, Band, **band_attrs)
            if band_created:
                session.commit()
                # TODO: Actually do the physical work to tile it
            else:
                print("Already have in database...")

    from IPython.core.debugger import Pdb; Pdb().set_trace()
