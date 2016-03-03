""" Logic for adding/editing/getting entries in tables
"""
from tilezilla.db._util import get_or_add
from tilezilla.db.sqlite.tables import (TileSpec, Collection, Tile, Product,
                                        Band)


class DatacubeResource(object):
    """ Tiles of products for a given tile specification
    """

    def __init__(self, db, tilespec):
        self._db = db
        self.tilespec = tilespec
        self.init()

# TileSpec management
    def init(self):
        defaults = dict(ul_x=self.tilespec.ul[0],
                        ul_y=self.tilespec.ul[1],
                        crs=self.tilespec.crs_str,
                        res_x=self.tilespec.res[0],
                        res_y=self.tilespec.res[1],
                        size_x=self.tilespec.size[0],
                        size_y=self.tilespec.size[1])
        kwargs = dict(desc=self.tilespec.desc)
        self._tilespec = get_or_add(self._db, TileSpec,
                                    defaults=defaults, **kwargs)

# Collection management
    def get_collection(self, _id):
        return (self._db.session.query(Collection)
                .filter(Collection.id == _id))

    def get_collection_by_name(self, name):
        return (self._db.session.query(Collection)
                .filter(Collection.name == name).first())

    def get_collections(self):
        return (self._db.session.query(Collection)
                .filter(TileSpec.id == self._tilespec.id).all())

    def search_collections(self, **kwargs):
        return self._db.query(Collection).filter_by(**kwargs).all()

    def add_collection(self, name):
        """ Create new collection if needed

        Args:
            name (str): Name of collection to add or retrieve
        Returns:
            bool: True if a new collection was created
        """
        defaults = dict(ref_tilespec_id=self._tilespec.id)
        kwargs = dict(name=name)
        return get_or_add(self._db, Collection, defaults=defaults, **kwargs)[1]

# Tile management
