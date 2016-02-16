import logging

from .version import __version__  # noqa


_FORMAT = '%(asctime)s:%(levelname)s:%(lineno)s:%(module)s.%(funcName)s:%(message)s'  # noqa
_formatter = logging.Formatter(_FORMAT, '%H:%M:%S')
_handler = logging.StreamHandler()
_handler.setFormatter(_formatter)

logger = logging.getLogger('tilezilla')
logger.addHandler(_handler)
logger.setLevel(logging.INFO)
