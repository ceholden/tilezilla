from contextlib import contextmanager

import sqlalchemy as sa

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
        engine = sa.create_engine(uri, echo=debug)
        Base.metadata.create_all(engine)
        session = sa.orm.sessionmaker(bind=engine)()

        return cls(engine, session)

    @classmethod
    def from_config(cls, config=None):
        # http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls
        config = config or {}
        uri_config = {
            'drivername': config.get('drivername'),
            'database': config.get('database'),
            'username': config.get('username', '') or None,
            'password': config.get('password', '') or None,
            'host': config.get('host', '') or None,
            'port': config.get('port', '') or None
        }

        return cls.connect(
            uri=sa.engine.url.URL(**uri_config),
            debug=config.get('debug', False)
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
