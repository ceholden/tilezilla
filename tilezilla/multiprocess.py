""" Multiprocess helpers
"""
# LOGGING FOR MULTIPROCESSING
MULTIPROC_LOG_FORMAT = '%(asctime)s:%(hostname)s:%(process)d:%(levelname)s:%(message)s'  # noqa
MULTIPROC_LOG_DATE_FORMAT = '%H:%M:%S'


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
    import logging
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
class SerialExecutor(object):
    """ Make regular old 'map' look like :mod:`futures.concurrent`
    """
    map = map

    def submit(self, func, *args, **kwargs):
        return func(*args, **kwargs)

    @staticmethod
    def result(value):
        return value

    def shutdown(self, wait=True):
        pass

    def __enter__(self):
        return self

    def __exit__(self):
        self.shutdown()
        return False


def get_executor(executor, njob):
    """ Return an instance of a execution mapper

    Args:
        executor (str): Name of execution method to return
        njob (int): Number of jobs to use in execution

    Returns:
        cls: Instance of a pool executor

    """
    if executor.lower() == 'process':
        from concurrent.futures import ProcessPoolExecutor
        return ProcessPoolExecutor(njob)
    else:
        return SerialExecutor()


MULTIPROC_METHODS = [
    'serial',
    'process',
    # TODO: ipyparallel for distributed across network
]
