import os
from setuptools import find_packages, setup

# Get version
with open(os.path.join('tilezilla', 'version.py')) as f:
    for line in f:
        if line.find('__version__') >= 0:
            version = line.split("=")[1].strip()
            version = version.strip('"').strip("'")
            continue

install_requires = [
    'click',
    'click_plugins',
    'numpy',
    'rasterio',
    'shapely'
]

entry_points = '''
    [console_scripts]
    tilez=tilezilla.cli.main:cli

    [tilez.commands]
    ingest=tilezilla.cli.ingest:ingest
    spew=tilezilla.cli.spew:spew
    shapes=tilezilla.cli.info:shapes
'''

setup(
    name='tilezilla',
    version=version,
    packages=find_packages(),
    package_data={'tilezilla': ['data/']},
    include_package_data=True,
    install_requires=install_requires,
    entry_points=entry_points
)
