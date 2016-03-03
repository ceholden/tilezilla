""" Common utility functions
"""


def get_or_add(db, model, defaults=None, **kwargs):
    """ Return instance of `model` from `db`, creating if necessary

    Args:
        db (db._db.Database): Database connection
        model (class): A table model to retrieve from the database `db`
        defaults (dict): Dictionary of default parameters for `model`
        kwargs (dict): Keyword arguments that parametrize `model` in the
            database `db`. These are also used in creation of new instance,
            if needed.

    Returns:
        tuple[model, bool]: Return instance of `model` and boolean indicating
            if the instance was added to the database.
    """
    instance = db.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        kwargs.update(defaults or {})
        instance = model(**kwargs)
        with db.scope() as session:
            session.add(instance)
        return instance, True
