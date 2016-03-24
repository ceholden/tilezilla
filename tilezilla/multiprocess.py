""" Multiprocess helpers
"""


class SerialExecutor(object):
    """ Make regular old 'map' look like :mod:`futures.concurrent`
    """
    map = map


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
