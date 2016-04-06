import pytest

from tilezilla.sensors import landsat


@pytest.mark.parametrize(('sensor', 'desc', 'answer'), [
    ('LT4', 'band 1 reflectance', 'blue'),
    ('LT5', 'band2', 'green'),
    ('LE7', 'band_4', 'nir'),
    ('LT4', 'BAND_40', 'nir'),
    ('LC8', 'band6', 'swir1'),
    ('LC8', 'band7', 'swir2'),
    ('LC8', 'band 3 surface reflectance', 'green'),
    ('LT4', 'QA', 'QA'),  # qa/qc band
    ('LC8', 'band 1', 'band 1')  # new coastal
])
def test_description_to_friendly_name(sensor, desc, answer):
    test = landsat.description_to_friendly_name(sensor, desc)
    assert test == answer


def test_parse_MTL(MTL_file, MTL_data, MTL_from_file):
    test = landsat.parse_MTL(MTL_file)
    assert test == MTL_data


def test_MTL(MTL_file, MTL_data):
    mtl = landsat.MTL.from_file(MTL_file)

    assert mtl.scene_id == MTL_data['LANDSAT_SCENE_ID']
    assert mtl.LPGS == MTL_data['PROCESSING_SOFTWARE_VERSION']
    assert mtl.product_level == MTL_data['DATA_TYPE']
    assert mtl.sensor == MTL_data['SPACECRAFT_ID']
    assert mtl.path_row == (MTL_data['WRS_PATH'], MTL_data['WRS_ROW'])
    assert mtl.cloud_cover == float(MTL_data['CLOUD_COVER'])


# TODO: test ESPAMetadata
