""" Test utilities for ensuring the correctness of products
"""
import arrow
import six

from tilezilla.core import BoundingBox, Band


MAPPING = {
    'timeseries_id': six.string_types,
    'acquired': arrow.Arrow,
    'processed': arrow.Arrow,
    'platform': six.string_types,
    'instrument': six.string_types,
    'bounds': BoundingBox,
    'bands': [Band],
    'metadata': dict,
    'metadata_files': dict
}


def check_attributes(product):
    for attr, _type in six.iteritems(MAPPING):
        assert hasattr(product, attr)
        value = getattr(product, attr)

        if isinstance(_type, (type, tuple)):
            # Type declaration one or more types
            assert isinstance(value, _type)
        else:
            # Type declaration list of types
            assert isinstance(value, type(_type))
            for item in value:
                assert isinstance(item, tuple(_type))
