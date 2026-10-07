import geopandas as gpd
from shapely.geometry import Point

from app.services.crs import projected_gdf


def test_geographic_crs_is_projected():
    gdf = gpd.GeoDataFrame(
        {"name": ["test"]},
        geometry=[Point(77.5946, 12.9716)],
        crs="EPSG:4326",
    )
    result = projected_gdf(gdf)
    assert result.crs.is_projected


def test_projected_crs_is_preserved():
    gdf = gpd.GeoDataFrame(
        {"name": ["test"]},
        geometry=[Point(500000, 1430000)],
        crs="EPSG:32643",
    )
    result = projected_gdf(gdf)
    assert result.crs == gdf.crs
