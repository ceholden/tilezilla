""" Tools for storing data cube tiles
"""
import inspect
import os

from .geotiff import GeoTIFFStore
from .vrt import VRT

STORAGE_TYPES = {
    'GeoTIFF': GeoTIFFStore,
    # TODO: 'NetCDF': NetCDFStore
}

__all__ = [
    'GeoTIFFStore',
    'VRT'
]


def destination_path(config, tile, product, root_override=None):
    """ Return path to tile data directory

    Tile data dairectory is constructed as follows:

    [root]/[collection name]/[tile name]

    Args:
        config (dict): Tilezilla configuration file information
        tile (Tile): Retrieve destination for this tile
        product (BaseProduct): Retrieve destination for this product
        root_override (str): If specified, override root directory found in
            configuration

    Returns:
        str: Product destination root folder
    """
    root = root_override or config['store']['root']
    tile_part = tile.str_format(config['store']['tile_dirpattern'])

    return os.path.join(root, product.description, tile_part)
