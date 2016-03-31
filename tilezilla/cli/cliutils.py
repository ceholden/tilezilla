import logging

import click


def config_to_resources(config):
    """ Return `tilezilla` resources from a configuration dict

    Args:
        config (dict): `tilezilla` configuration

    Return:
        tuple[TileSpec, str, Database, DatacubeResource, DatasetResource]: A
            collection of resources for checking, indexing, and tiling data
    """
    from ..db import Database, DatacubeResource, DatasetResource
    spec = config['tilespec']
    store_name = config['store']['name']
    db = Database.from_config(config['database'])
    datacube = DatacubeResource(db, spec, store_name)
    dataset = DatasetResource(db, datacube)
    return spec, store_name, db, datacube, dataset


class Echoer(object):
    """ Stylistic wrapper around loggers for communicating with user

    Communication methods:

        1. process: announce beginning of some process (logging.INFO)
        2. item: progress within a process for an item (logging.INFO)
        3. info: general information (logging.INFO)
        4. warnings: warnings, less severe than errors (logging.WARNING)
        5. error: errors (logging.ERROR)

    """
    STYLE = {
        'process': '==>'.ljust(1),
        'item': '-'.ljust(7),
        'info': '*'.ljust(3),
        'warning': 'X'.ljust(3),
        'error': 'X'.ljust(3)
    }

    def __init__(self, logger=None, prefix=''):
        self.logger = logger or logging.getLogger(logger)
        self.prefix = prefix

    def process(self, msg, **kwargs):
        """ Print a message about a process
        """
        msg = click.style(msg, **kwargs)
        pre = click.style(self.prefix + self.STYLE['process'],
                          fg='blue', bold=True)

        self.logger.info(pre + msg)

    def item(self, msg, **kwargs):
        """ Print a progress message for an  item
        """
        msg = click.style(msg, **kwargs)
        pre = click.style(self.prefix + self.STYLE['item'], fg='green')

        self.logger.info(pre + msg)

    def info(self, msg, fg='black', **kwargs):
        """ Print an info message
        """
        msg = click.style(msg, **kwargs)
        pre = click.style(self.prefix + self.STYLE['info'], bold=True)

        self.logger.info(pre + msg)

    def warning(self, msg, fg='red', **kwargs):
        """ Print a warning message
        """
        msg = click.style(msg, fg='yellow', **kwargs)
        pre = click.style(self.prefix + self.STYLE['warning'],
                          fg='yellow', bold=True)

        self.logger.warning(pre + msg)

    def error(self, msg, fg='red', **kwargs):
        """ Print an error message
        """
        msg = click.style(msg, **kwargs)
        pre = click.style(self.prefix + self.STYLE['error'],
                          fg='red', bold=True)

        self.logger.error(pre + msg)
