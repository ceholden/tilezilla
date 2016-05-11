""" Test utilities for ensuring the correctness of products
"""
import arrow
import six

from tilezilla.core import BoundingBox, Band


MAPPING = {
    'timeseries_id': str,
    'acquired': arrow.Arrow,
    'processed': arrow.Arrow,
    'platform': str,
    'instrument': str,
    'bounds': BoundingBox,
    'bands': [Band],
    'metadata': dict,
    'metadata_files': dict
}


def check_attributes(product):
    for attr, _type in six.iteritems(MAPPING):
        assert hasattr(product, attr)
        value = getattr(product, attr)

        if isinstance(_type, type):
            assert isinstance(value, _type)
        else:
            assert isinstance(value, type(_type))
            for item in value:
                assert isinstance(item, tuple(_type))
