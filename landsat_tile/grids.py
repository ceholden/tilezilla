""" Predefined grids and utilities for working with grid systems
"""
import json
import pkgutil

_grid_data = pkgutil.get_data('landsat_tile', 'data/grids.json')
GRIDS = json.loads(_grid_data)
