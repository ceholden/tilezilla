""" Tools for storing data cube tiles
"""
from .geotiff import GeoTIFFStore

STORAGE_TYPES = {
    'GeoTIFF': GeoTIFFStore,
    # TODO: 'NetCDF': NetCDFStore
}
