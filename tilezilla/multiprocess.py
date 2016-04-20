""" Multiprocess helpers
"""
import logging

# LOGGING FOR MULTIPROCESSING
MULTIPROC_LOG_FORMAT = '%(asctime)s:%(hostname)s:%(process)d:%(levelname)s:%(message)s'  # noqa
MULTIPROC_LOG_DATE_FORMAT = '%H:%M:%S'

_LOG = logging.getLogger(__name__)


def get_logger_multiproc(name=None, filename='', stream='stdout'):
    """ Return a logger configured/styled for multi-processing

    Args:
        name (str): Name of logger to retrieve/configure
        filename (str): Log to this filename using :class:`logging.FileHandler`
        stream (str): Name of stream to use with logger. If `stream` is
            specified with `filename`, then the `stream` argument is ignored.

    Returns:
        logging.LoggerAdapter: A configured logger
    """
    import socket
    import click

    class ClickFileHandler(logging.FileHandler):
        def emit(self, record):
            try:
                msg = self.format(record)
                err = record.levelno > 20
                click.echo(msg, file=self.stream, err=err)
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                self.handleError(record)


    logger = logging.getLogger(name)
    formatter = logging.Formatter(MULTIPROC_LOG_FORMAT,
                                  MULTIPROC_LOG_DATE_FORMAT)

    if filename:
        handler = ClickFileHandler(filename, 'w')
    else:
        stream = click.get_text_stream(stream)
        handler = logging.StreamHandler(stream)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.setLevel(logging.DEBUG)

    extra = {'hostname': socket.gethostname()}
    logger_adapter = logging.LoggerAdapter(logger, extra)

    return logger_adapter


# MULTIPROCESSING
def get_executor(executor, njob):
    """ Return an instance of a execution mapper

    Args:
        executor (str): Name of execution method to return
        njob (int): Number of jobs to use in execution

    Returns:
        cls: Instance of a pool executor

    """
    try:
        from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
    except ImportError:
        _LOG.critical('You must have Python3 or "futures" package installed.')
        raise
    if executor.lower() == 'process':
        return ProcessPoolExecutor(njob)
    elif executor.lower() == 'thread':
        _LOG.warning('Un-tested executor for multiprocessing')
        return ThreadPoolExecutor(njob)
    else:
        return ThreadPoolExecutor(1)  # serial


MULTIPROC_METHODS = [
    'serial',
    'process',
    # TODO: ipyparallel for distributed across network
    # TODO: note that ipyparallel can give us a "Futures" result:
    # https://github.com/ipython/ipyparallel/blob/58136e8d727967f0783c4c003ba54e3ca1879fbf/examples/Futures.ipynb
]
