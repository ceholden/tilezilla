from tilezilla.db._db import Database
from tilezilla.db._util import get_or_add
from tilezilla.db._resources import DatacubeResource, DatasetResource
from tilezilla.db.sqlite.tables import (
    TableTileSpec, TableTile, TableProduct, TableBand)


if __name__ == '__main__':
    from tilezilla import tilespec, products, stores, _util

    # Create a product
    prod = products.ESPALandsat.from_path('tests/data/LT50120312002300-SC20151009172149_EPSG5070/')

    products = [prod]

    # Get the database
    db = Database.from_config()
    # Create the tile specification
    weld_conus = tilespec.TILESPECS['WELD_CONUS']
    # Create datacube resource
    storage = 'GeoTIFFStore'
    datacube = DatacubeResource(db, weld_conus, storage)
    # Create dataset resource
    dataset = DatasetResource(db, datacube)
    # Add / get collection
    collection_name = prod.description
    datacube.ensure_collection(collection_name)

    # Create/get collection for product
    include_pattern = {
        'long_name': ('.*surface reflectance.*',
                      '.*brightness temperature.*',
                      '^cfmask_band$')
    }
    desired_bands = _util.include_bands(prod.bands,
                                        include_pattern, regex=True)

    for product in products:
        product_ids = dataset.ensure_product(product)
        for product_id in product_ids:
            for band in product.bands:
                dataset.ensure_band(product_id, band)

    from IPython.core.debugger import Pdb; Pdb().set_trace()
