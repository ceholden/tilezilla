""" Helpers for guessing our way into queries against the database
"""
import sqlalchemy as sa
import sqlalchemy_utils as sau



def convert_query_type(table, key, value):
    """ Return `value` converted to type expected by `table` for column `key`

    Args:
        table (): A SQLAlchemy ORM table
        key (str): A column name in `table`
        value (str): A value to convert

    Returns:
        type: `value`, converted to a different type
    """
    c = getattr(table, key, None)
    if c is None:
        raise KeyError('{} not a column in {}'.format(key, table))
    from IPython.core.debugger import Pdb; Pdb().set_trace()
    return sau.cast_if(value, type(c.type))
