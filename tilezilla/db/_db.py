from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .sqlite.tables import Base


class Database(object):
    """ The database connection
    """
    def __init__(self, engine, session):
        self.engine = engine
        self.session = session

    @classmethod
    def connect(cls, uri, debug=False):
        """ Return a Database for a given URI

        Args:
            URI (str): Resource location
            debug (bool): Turn on sqlalchemy debug echo

        Returns:
            Database
        """
        engine = create_engine(uri, echo=debug)
        Base.metadata.create_all(engine)
        session = sessionmaker(bind=engine)()

        return cls(engine, session)

    @classmethod
    def from_config(cls, config=None):
        config = config or {}
        uri = '{driver}:///{uri}'.format(driver=config.get('driver'),
                                         uri=config.get('uri', 'tilezilla.db'))
        return cls.connect(
            uri=uri,
            debug=config.get('debug', True)
        )

    def scope(self):
        """ Session as a context manager

        Intended to be used as follows:

        ..code-block:: python

            with db.scope() as scope:
                # do stuff

        """
        @contextmanager
        def _scope():
            try:
                yield self.session
                self.session.commit()
            except:
                self.session.rollback()
                raise
        return _scope()
