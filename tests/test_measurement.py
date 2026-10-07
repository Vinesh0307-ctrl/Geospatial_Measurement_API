from shapely.geometry import LineString, Point, Polygon

from app.services.measurement import calculate_measurement


def test_polygon_area():
    result = calculate_measurement(Polygon([(0, 0), (2, 0), (2, 2), (0, 2)]))
    assert result["area"] == 4.0
    assert result["unit"] == "m²"


def test_linestring_length():
    result = calculate_measurement(LineString([(0, 0), (3, 4)]))
    assert result["length"] == 5.0
    assert result["unit"] == "m"


def test_point_has_no_measurement():
    assert calculate_measurement(Point(1, 2)) is None
