import os
import pickle

import pytest

HERE = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def MTL_file(request):
    return os.path.join(HERE, 'data', 'LT40130301987146XXX01_MTL.txt')


@pytest.fixture
def MTL_data(request):
    p = os.path.join(HERE, 'data', 'LT40130301987146XXX01_MTL.txt.pkl')
    with open(p, 'rb') as f:
        return pickle.loads(f.read())


@pytest.fixture
def MTL_from_file():
    def inner(filename):
        from collections import OrderedDict
        with open(filename, 'r') as f:
            data = OrderedDict()
            for line in f:
                split = line.split(' = ')
                if len(split) == 2:
                    data[split[0].strip().strip('"')] = \
                        split[1].strip().strip('"')
            return data
    return inner
