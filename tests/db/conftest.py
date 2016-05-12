""" Database test resources

References:
- http://stackoverflow.com/questions/34080083/how-to-combine-py-test-fixtures-with-flask-sqlalchemy-and-postgresql
- http://stackoverflow.com/questions/28526781/isolating-py-test-db-sessions-in-flask-sqlalchemy
- http://alextechrants.blogspot.com/2013/08/unit-testing-sqlalchemy-apps.html
- http://piotr.banaszkiewicz.org/blog/2014/02/22/how-to-bite-flask-sqlalchemy-and-pytest-all-at-once/#testing-everything
- http://alexmic.net/flask-sqlalchemy-pytest/
"""
import sqlalchemy as sa
import pytest

from tilezilla.db import _tables

SESSION_URI = 'sqlite://'


@pytest.fixture(scope='session')
def engine():
    return sa.create_engine(SESSION_URI)


@pytest.yield_fixture(scope='session')
def tables(engine):
    _tables.Base.metadata.create_all(engine)
    yield
    _tables.Base.metadata.drop_all(engine)


@pytest.yield_fixture
def session(engine, tables):
    connection = engine.connect()
    transaction = connection.begin()
    session = sa.orm.Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
