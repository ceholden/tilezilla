import pytest

from tilezilla import tilespec


@pytest.fixture
def example_spec(request):
    for k in tilespec.TILESPECS:
        return tilespec.TILESPECS[k]


# tilezilla.tilespec.TileSpec
@pytest.mark.parametrize(('ul', 'crs', 'res', 'size', 'desc'), [
    ((0., 0.), 'epsg:4326', (0.00025, 0.0025), (1., 1.), 'geographic'),
    ((-2565600., 3314800.), 'epsg:5070', (30, 30), (250, 250), 'albers_conus'),
    ((653385., 4828815.), 'epsg:32619', (30, 30), (5000, 5000), 'utm19n')
])
def test_tilespec(ul, crs, res, size, desc):
    tilespec.TileSpec(ul, crs, res, size, desc=desc)


def test_tilespec_fail_1(example_spec):
    with pytest.raises(IndexError):
        example_spec[-1]


def test_tilespec_fail_2(example_spec):
    with pytest.raises(TypeError):
        example_spec[([0, 1], [0, 1])]
    assert False
