# flake8: noqa

%load_ext autoreload
%autoreload 2
% connect_info

# Imports
import inspect
import json

import rasterio
from rasterio import crs, warp
import shapely

import tilezilla
from tilezilla import geoutils, products, stores, tilespec

# Get tilespec, find product, retrieve intersecting tiles
weld_conus = tilespec.TILESPECS['WELD_CONUS']
product = products.ESPALandsat('../tests/data/LT50120312002300-SC20151009172149/')

tile = list(weld_conus.bounds_to_tile(product.bounding_box(weld_conus.crs)))[0]

crs.to_string(weld_conus.crs)
weld_conus.crs


geoutils.bounds_to_polygon(tile.bounds)

# TODO: geom_geojson looks a little off
warp.transform_geom('EPSG:4326', 'EPSG:5070', json.dumps(tile.geom_geojson))


# Init the data store
# TODO: switch on some storage format metadata configuration values
store = stores.GeoTIFFStore('tests/data/stores/GeoTIFF', tile, product)

# TODO: allow override driver metadata options (section "creation_options:")
store.meta_options

# TODO: user input / configuration to define desired variables
to_store = _util.multiple_filter(
    [b.long_name for b in product.bands],
    ('.*surface reflectance.*', '.*brightness temperature.*', '^cfmask_band$',),
    True)
to_store

for band in [b for b in product.bands if b.long_name in to_store]:
    band.src = geoutils.reproject_as_needed(band.src, weld_conus)
    band.band = rasterio.band(band.src, band.bidx)
    store.store_variable(band)
store.path

{k: v for k, v in inspect.getmembers(tile.__class__) if not inspect.ismethod(v)}
inspect.getmembers(tile)
