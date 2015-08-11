from setuptools import find_packages, setup

# Get version
with open('landsat_tile/version.py') as f:
    for line in f:
        if line.find('__version__') >= 0:
            version = line.split("=")[1].strip()
            version = version.strip('"')
            version = version.strip("'")
            continue

install_requires = [
    'click',
    'click_plugins',
    'numpy'
]

entry_points = '''
    [console_scripts]
    landsat_tile=landsat_tile.cli.main:cli

    [landsat_tile.commands]
    prepare=landsat_tile.cli.prepare:prepare
    unzip=landsat_tile.cli.cli:unzip
    tile_bounds=landsat_tile.cli.cli:tile_bounds
    warp=rasterio.rio.warp:warp
    batch=landsat_tile.cli.cli:batch
'''

setup(
    name='landsat_tile',
    version=version,
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    entry_points=entry_points
)
