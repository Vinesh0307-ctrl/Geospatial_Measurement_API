import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.models.schemas import FileInfoResponse, MeasurementResponse
from app.services.file_processor import process_geospatial_file

router = APIRouter(tags=["files"])

STORAGE = Path("uploads")
STORAGE.mkdir(exist_ok=True)

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
_file_store: dict[str, dict] = {}


@router.post(
    "/files/",
    response_model=FileInfoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename or ""
    suffix = Path(filename).suffix.lower()

    if suffix not in {".kml", ".zip"}:
        raise HTTPException(
            status_code=400,
            detail="Only .kml and .zip files are supported.",
        )

    content = await file.read()

    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the 50 MB upload limit.",
        )

    file_id = uuid.uuid4().hex[:12]
    saved_path = STORAGE / f"{file_id}{suffix}"
    saved_path.write_bytes(content)

    try:
        result = process_geospatial_file(saved_path)

        _file_store[file_id] = {
            "id": file_id,
            "filename": filename,
            "feature_count": result["feature_count"],
            "crs": result["crs"],
            "status": "COMPLETED",
            "measurements": result["measurements"],
        }

        return _file_store[file_id]

    except ValueError as exc:
        saved_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    except Exception as exc:
        saved_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to process geospatial file.",
        ) from exc


@router.get(
    "/files/{file_id}/",
    response_model=FileInfoResponse,
)
def file_information(file_id: str):
    item = _file_store.get(file_id)

    if not item:
        raise HTTPException(status_code=404, detail="File not found.")

    return item


@router.get(
    "/files/{file_id}/measurements/",
    response_model=MeasurementResponse,
)
def measurements(file_id: str):
    item = _file_store.get(file_id)

    if not item:
        raise HTTPException(status_code=404, detail="File not found.")

    return {
        "file_id": file_id,
        "features": item["measurements"],
    }
