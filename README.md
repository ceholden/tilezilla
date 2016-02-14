# landsat_tile

## STATUS: IN REDEVELOPMENT

## About

Convert Landsat products (Level 1 or Climate Data Record) into roughly 1°x1° tiles suitable for large scale mapping beyond traditional WRS-2 path and row or UTM zone boundaries. Input images can be reprojected into a suitable projection and grid to mimic pre-existing products (e.g., [National Land Cover Database (NLCD)](http://www.mrlc.gov/index.php)) or users can define their own projection and grid. Timeseries assembled from such tiles can easily incorporate observations from multiple viewing geometries by taking advantage of "sidelap" areas in adjacent WRS-2 paths.

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
$ Usage: landsat_tile [OPTIONS] COMMAND [ARGS]...

  Landsat tile preprocessing command line interface (CLI)

Options:
  --version      Show the version and exit.
  -v, --verbose  Be verbose
  -q, --quiet    Be quiet
  -h, --help     Show this message and exit.

Commands:
  ingest  Ingest known products into tile dataset format
  shapes  Get shapes of tiled datasets
  spew    Export tile dataset to other dataset format

```

## Installation

### Anaconda

The easiest way to install `landsat_tile` is to use the [`conda` package manager](http://conda.pydata.org/docs/index.html) from the [Anaconda project](https://www.continuum.io/why-anaconda) by [Continuum Analytics](https://www.continuum.io/). You can grab `conda` either through the full `Anaconda` installer or using the `miniconda` installer from their [downloads page](https://www.continuum.io/downloads).

With `conda` installed, you can install all dependendies of `landsat_tile` into an isolated environment using the `conda env` subcommand:

``` bash
# Create environment
$ conda env create -f environment.yaml
# Activate environment
$ source activate landsat_tile
# Install landsat_tile
$ pip install .
```

### Development

If you are interested in developing `landsat_tile`, I suggest installing via `pip` with the `-e` flag to create an editable installation. For installation instructions for developing `landsat_tile` using the [`click`](http://click.pocoo.org/) command line interface library, see [`click`'s setuptools installation instructions](http://click.pocoo.org/5/setuptools/).
