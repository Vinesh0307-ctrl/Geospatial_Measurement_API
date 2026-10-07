from typing import Any

from pydantic import BaseModel, Field


class FileInfoResponse(BaseModel):
    id: str
    filename: str
    feature_count: int = Field(ge=0)
    crs: str
    status: str


class FeatureResponse(BaseModel):
    feature_id: int
    geometry_type: str
    geometry: dict[str, Any]
    crs: str
    properties: dict[str, Any]
    measurement: dict[str, Any] | None


class MeasurementResponse(BaseModel):
    file_id: str
    features: list[FeatureResponse]
