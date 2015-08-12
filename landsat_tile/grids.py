""" Predefined grids and utilities for working with grid systems

TODO: move this to a json file (?)

"""

# Grids are defined as a dictionary of projection / geotransform parameters
# listed in the style of `rasterio`
grids = {

    # NLCD 1992: http://webmap.ornl.gov/ogcdown/wcsdown.jsp?dg_id=10009_21
    'nlcd1992': {
        # http://spatialreference.org/ref/sr-org/albers-conical-equal-area-as-used-by-mrlcgov-nlcd/
        # 'crs': '+proj=aea +lat_0=23 +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs',
        'crs': '+ellps=GRS80 +lat_0=23 +lat_1=29.5 +lat_2=45.5 +lon_0=-96 +no_defs +proj=aea +towgs84=0,0,0,0,0,0,0 +units=m +x_0=0 +y_0=0',
        # Spatial Extent: N: 3177735, S: 267885, E: 2266005, W: -2361915
        'bounds': [-2361915.0, 267885.0, 2266005.0, 3177735],
        'res': [30, 30]
    }

}



