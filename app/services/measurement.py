def calculate_measurement(geometry):
    geometry_type = geometry.geom_type

    if geometry_type in {"Polygon", "MultiPolygon"}:
        return {
            "area": round(float(geometry.area), 6),
            "unit": "m²",
        }

    if geometry_type in {"LineString", "MultiLineString"}:
        return {
            "length": round(float(geometry.length), 6),
            "unit": "m",
        }

    if geometry_type == "Point":
        return None

    return {
        "supported": False,
        "message": f"Measurement is not supported for {geometry_type}.",
    }
