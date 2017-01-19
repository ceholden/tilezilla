""" Export multiband imagery in VRT compatibility format

NOTES:
    * Obviously works with GeoTIFF store format
    * Seems to work with NetCDF format as long as the NetCDF dataset is
      properly georeferenced (i.e., use clover to make sure it is!)
"""
from collections import defaultdict
import os
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ElementTree, Element, SubElement
from xml.dom import minidom

from rasterio import dtypes

COLOR_INTERP = defaultdict(str)
COLOR_INTERP[2] = 'Red'
COLOR_INTERP[1] = 'Green'
COLOR_INTERP[0] = 'Blue'


class VRT(object):
    """ Create a VRT from a band in one or more datasets

    Only inteded right now to assist in visualizing (i.e., in QGIS) with
    multiple `Band`s from one `BaseProduct` within one `Tile`.

    Args:
        datasets (list[RasterReader]): `rasterio` raster dataset
        bidx (list[int]): Band indices of `datasets` to include
    """
    def __init__(self, datasets, bidx):
        self._validate(datasets)
        # Create root
        self.root = Element('VRTDataset')
        self.root.set('rasterXSize', str(datasets[0].width))
        self.root.set('rasterYSize', str(datasets[0].height))
        # Add CRS & GeoTransform
        self.crs = self._add_crs(datasets[0])
        self.geotransform = self._add_geotransform(datasets[0])
        # Add bands
        self.bands = []
        for idx, (ds, _bidx) in enumerate(zip(datasets, bidx)):
            self.bands.append(self._add_band(idx, ds, _bidx))

    def write(self, path):
        """ Save VRT XML data to a filename

        Args:
            path (str): Save VRT to this filename
        """
        xmlstr = (minidom.parseString(ET.tostring(self.root))
                  .toprettyxml(indent='    '))
        with open(path, 'w') as fid:
            fid.write(xmlstr)

    def _add_crs(self, ds):
        crs = SubElement(self.root, 'SRS')
        crs.text = ds.crs.wkt

        return crs

    def _add_geotransform(self, ds):
        gt = SubElement(self.root, 'GeoTransform')
        gt.text = ', '.join(map(str, ds.transform.to_gdal()))

        return gt

    def _add_band(self, idx, ds, bidx):
        """ Add a band to VRT

        Args:
            idx (int): Index of band in VRT
            ds (RasterReader): `rasterio` dataset
            bidx (int): Band index of `ds`
        """
        band = SubElement(self.root, 'VRTRasterBand')
        band.set('dataType', dtypes._gdal_typename(ds.dtypes[bidx - 1]))
        band.set('band', str(idx + 1))
        # Color interpretation
        ci = SubElement(band, 'ColorInterp')
        ci.text = COLOR_INTERP[idx]
        # Add NoDataValue
        if ds.nodatavals:
            ndv = SubElement(band, 'NoDataValue')
            ndv.text = str(ds.nodatavals[bidx - 1])
        # Add SimpleSource
        source = SubElement(band, 'SimpleSource')
        source_path = SubElement(source, 'SourceFilename')
        source_path.text = os.path.abspath(ds.name)
        source_props = SubElement(source, 'SourceProperties')
        source_props.set('RasterXSize', str(ds.width))
        source_props.set('RasterYSize', str(ds.height))
        source_props.set('DataType', dtypes._gdal_typename(ds.dtypes[bidx - 1]))
        source_props.set('BlockXSize', str(ds.block_shapes[bidx - 1][1]))
        source_props.set('BlockYSize', str(ds.block_shapes[bidx - 1][0]))

        return source

    def _validate(self, datasets):
        # Check size
        width, height = datasets[0].width, datasets[0].height
        for _ds in datasets:
            if (width, height) != (_ds.width, _ds.height):
                raise ValueError('All datasets must be the same size')
        # Check projection
        crs = datasets[0].crs
        for _ds in datasets:
            if crs != _ds.crs:
                raise ValueError('All datasets must have same CRS')
