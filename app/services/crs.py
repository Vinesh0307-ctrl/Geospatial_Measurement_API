import geopandas as gpd


def projected_gdf(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    if gdf.crs is None:
        raise ValueError(
            "Input data has no CRS. A CRS is required for accurate measurements."
        )

    if gdf.crs.is_projected:
        return gdf

    try:
        estimated = gdf.estimate_utm_crs()
    except Exception as exc:
        raise ValueError("Could not determine a suitable projected CRS.") from exc

    if estimated is None:
        raise ValueError("Could not determine a suitable projected CRS.")

    return gdf.to_crs(estimated)
