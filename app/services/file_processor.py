from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import BadZipFile, ZipFile

import geopandas as gpd
import pandas as pd

from app.services.crs import projected_gdf
from app.services.measurement import calculate_measurement


REQUIRED_SHAPEFILE_PARTS = {".shp", ".shx", ".dbf"}


def _make_json_safe(value):
    if value is None:
        return None

    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        try:
            return value.item()
        except (ValueError, AttributeError):
            pass

    if hasattr(value, "isoformat"):
        return value.isoformat()

    return value


def _safe_extract(zip_path: Path, destination: Path) -> Path:
    try:
        with ZipFile(zip_path) as archive:
            members = archive.namelist()

            if any(
                Path(member).is_absolute() or ".." in Path(member).parts
                for member in members
            ):
                raise ValueError("ZIP archive contains unsafe paths.")

            shp_members = [
                member for member in members
                if member.lower().endswith(".shp")
            ]

            if not shp_members:
                raise ValueError(
                    "ZIP archive does not contain a Shapefile (.shp)."
                )

            selected_stem = Path(shp_members[0]).with_suffix("")
            selected_prefix = str(selected_stem).replace("\\", "/")

            related_extensions = {
                Path(member).suffix.lower()
                for member in members
                if Path(member).with_suffix("").as_posix()
                == selected_prefix
            }

            missing = REQUIRED_SHAPEFILE_PARTS - related_extensions
            if missing:
                missing_text = ", ".join(sorted(missing))
                raise ValueError(
                    f"Shapefile is incomplete. Missing: {missing_text}."
                )

            archive.extractall(destination)

            extracted = destination / shp_members[0]
            if not extracted.exists():
                raise ValueError("Shapefile could not be extracted.")

            return extracted

    except BadZipFile as exc:
        raise ValueError("Uploaded ZIP file is invalid.") from exc


def _load_gdf(path: Path) -> gpd.GeoDataFrame:
    if path.suffix.lower() == ".kml":
        try:
            return gpd.read_file(path, driver="KML")
        except Exception as exc:
            raise ValueError("Could not read the KML file.") from exc

    with TemporaryDirectory() as tmp:
        shp_path = _safe_extract(path, Path(tmp))

        try:
            return gpd.read_file(shp_path)
        except Exception as exc:
            raise ValueError("Could not read the Shapefile.") from exc


def process_geospatial_file(path: Path) -> dict:
    gdf = _load_gdf(path)

    if gdf.empty:
        raise ValueError("The geospatial file contains no features.")

    if gdf.crs is None:
        raise ValueError(
            "Input data has no CRS. Include CRS information, "
            "such as a .prj file."
        )

    source_crs = gdf.crs
    source_crs_name = source_crs.to_string()

    measurement_gdf = projected_gdf(gdf)

    features = []

    for index in gdf.index:
        source_geometry = gdf.loc[index, "geometry"]
        measured_geometry = measurement_gdf.loc[index, "geometry"]

        properties = {
            column: _make_json_safe(gdf.loc[index, column])
            for column in gdf.columns
            if column != "geometry"
        }

        features.append(
            {
                "feature_id": int(index),
                "geometry_type": source_geometry.geom_type,
                "geometry": source_geometry.__geo_interface__,
                "crs": source_crs_name,
                "properties": properties,
                "measurement": calculate_measurement(measured_geometry),
            }
        )

    return {
        "feature_count": len(features),
        "crs": source_crs_name,
        "measurements": features,
    }
