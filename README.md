# landsat_tile
Utility for creating degree by degree tiles of Landsat data in some wide area projection

## Demo

As a demonstration of this project's output, I tiled a layer stacked Landsat 5 image over Boston:

``` bash
$ landsat_tile tile --grid nlcd1992 --mask --threads 4 --co "COMPRESS=LZW" LT50120312000183AAA02/LT50120312000183AAA02_stack.tif tiles/
*   Calculating intersecting tiles
*   Image intersects with 12 tiles
==> Creating image tiles
==> Tiling (-73.0, 41.0) to /home/ceholden/Documents/landsat_tiles/tiles/041N_073W/LT50120312000183AAA02/LT50120312000183AAA02_stack.tif
-   Masking to exactly tile extent
-   Reading in input image
-   Reprojecting all bands in image
...
==> Tiling (-70.0, 43.0) to /home/ceholden/Documents/landsat_tiles/tiles/043N_070W/LT50120312000183AAA02/LT50120312000183AAA02_stack.tif
-   Masking to exactly tile extent
-   Reading in input image
-   Reprojecting all bands in image
```

I opened the original image, the image tiles, and vector files that show the outline of the tiles created in QGIS as a demonstration:

![Demo](./docs/examples/demo.gif)

## Usage

`landsat_tile` contains several sub-commands that either help coordinate the tiling process (`batch`, `prepare`, `unzip`, and more) or actually perform the image tiling (`tile`). Currently, only the `tile` sub-command is implemented.

The full usage is:

``` bash
$ landsat_tile --help
Usage: landsat_tile [OPTIONS] COMMAND [ARGS]...

  Landsat tile preprocessing command line interface (CLI)

Options:
  --version      Show the version and exit.
  -v, --verbose  Be verbose
  -q, --quiet    Be quiet
  -h, --help     Show this message and exit.

Commands:
  batch    Batch tile a Landsat archive
  prepare  Create a JSON config file for batch processing
  tile     Subset to 1x1° tile, reproject, and align to grid one or more
           images
  unzip    Unzip and organize a Landsat dataset

```

The `tile` sub-command:

``` bash
$ landsat_tile tile --help
Usage: landsat_tile tile [OPTIONS] INPUT TILE_DIR

 Subset to 1x1° tile, reproject, and align to grid one or more images

 If --lon and --lat are not specified, the INPUT image will be split into
 all intersecting tiles. Tiles created will be saved under TILE_DIR in
 directories labeled according to the tile location. Directories for a given
 tile will contain tiled images within subdirectories labeled according to
 Landsat ID.

 Example:
     tiledir/
         41N_072W/
             LT50120312000183AAA02/
                 LT50120312000183AAA02_sr_band1.tif
         41N_073W/
             LT50120312000183AAA02/
                 LT50120312000183AAA02_sr_band1.tif

 Effort is made to copy metadata by setting the metadata on the destination
 image. Metadata come from the source data or source metadata (e.g., MTL
 files) next to input source images. Users can turn off this by specifying
 --no-metadata.

 TODO:
     1. Copy metadata (see docstring for details)
     2. Benchmark if faster to reproject each band individually, or read all bands in and then reproject

Options:
 --grid [nlcd1992]               Use bounds and CRS of a known product
 --grid-bounds FLOAT...          Grid bounds: left bottom right top
 --grid-crs TEXT                 Grid coordinate reference system.
 --grid-res FLOAT...             Grid X/Y resolution
 --ext TEXT                      Tile filename extension
 --mask                          Mask output to exactly 1x1°
 --ndv FLOAT                     Override source nodata value
 --dilate INTEGER                Number of pixels used to dilate tile bounds
                                 when masking  [default: 0]
 --lon #[W|E]                    Override upper left longitude of tile
 --lat #[N|S]                    Override upper left latitude of tile
 -of, --format TEXT              Output format driver  [default: GTiff]
 --co OPTION=VALUE               Driver creation options
 --resampling [nearest|bilinear|cubic|cubic_spline|lanczos|average|mode]
                                 Resampling method  [default: nearest]
 --threads INTEGER               Number of processing threads  [default: 1]
 --no-metadata                   Do not populate tile images with metadata
 --overwrite                     Overwrite destination file
 -h, --help                      Show this message and exit.
```

## Installation

You can install `landsat_tile` and its dependencies using [`pip`](https://pip.pypa.io/en/latest/installing.html). I also recommend installing `landsat_tile` into a [`virtualenv`](https://pypi.python.org/pypi/virtualenv).

``` bash
# Note the optional use of `system-site-packages` prevents duplicates of NumPy, etc.
$ virtualenv --system-site-packages venv
New python executable in venv/bin/python2
Also creating executable in venv/bin/python
Installing setuptools, pip, wheel...done.
# Enable virtualenv
$ source venv/bin/activate
(venv) $ pip install .
Obtaining file:///home/ceholden/Documents/landsat_tiles
Requirement already satisfied (use --upgrade to upgrade): click in /usr/lib/python2.7/site-packages (from landsat-tile==0.1.0)
Collecting click-plugins (from landsat-tile==0.1.0)
Requirement already satisfied (use --upgrade to upgrade): numpy in /usr/lib/python2.7/site-packages (from landsat-tile==0.1.0)
Requirement already satisfied (use --upgrade to upgrade): rasterio in /usr/lib/python2.7/site-packages (from landsat-tile==0.1.0)
Requirement already satisfied (use --upgrade to upgrade): affine>=1.0 in /usr/lib/python2.7/site-packages (from rasterio->landsat-tile==0.1.0)
Requirement already satisfied (use --upgrade to upgrade): cligj>=0.2.0 in /usr/lib/python2.7/site-packages (from rasterio->landsat-tile==0.1.0)
Requirement already satisfied (use --upgrade to upgrade): snuggs>=1.3.1 in /usr/lib/python2.7/site-packages (from rasterio->landsat-tile==0.1.0)
Requirement already satisfied (use --upgrade to upgrade): enum34 in /usr/lib/python2.7/site-packages (from rasterio->landsat-tile==0.1.0)
Requirement already satisfied (use --upgrade to upgrade): pyparsing in /usr/lib/python2.7/site-packages (from snuggs>=1.3.1->rasterio->landsat-tile==0.1.0)
Installing collected packages: click-plugins, landsat-tile
  Running setup.py develop for landsat-tile
Successfully instaf vlled click-plugins-1.0.1 landsat-tile
```

If you are interested in developing `landsat_tile`, I suggest installing via `pip` with the `-e` flag to create an editable installation. For installation instructions for developing `landsat_tile` using the [`click`](http://click.pocoo.org/) command line interface library, see [`click`'s setuptools installation instructions](http://click.pocoo.org/5/setuptools/).
