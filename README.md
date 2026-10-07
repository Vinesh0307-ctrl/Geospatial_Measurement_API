# Geospatial File Measurement API

A production-oriented FastAPI service for processing KML files and zipped ESRI Shapefiles and calculating measurements for supported geometries.

## Features

- KML upload
- ZIP/Shapefile upload
- Polygon and MultiPolygon area calculation
- LineString and MultiLineString length calculation
- Point support without measurement
- CRS validation
- Automatic local UTM projection for geographic CRS
- JSON-safe attribute serialization
- 50 MB upload limit
- ZIP path-traversal protection
- Shapefile component validation
- Graceful unsupported-geometry handling
- Typed FastAPI response models
- OpenAPI/Swagger documentation
- Unit and API integration tests
- Docker and Docker Compose support

## Tech Stack

- Python 3.11+
- FastAPI
- GeoPandas
- Shapely
- PyProj
- Fiona
- Pydantic
- Pytest
- Docker

## Architecture

```text
Client
  |
  v
FastAPI routes
  |
  +--> validation + file storage
  |
  v
File processor
  |
  +--> KML reader
  |
  +--> ZIP/Shapefile validation + extraction
  |
  v
GeoPandas GeoDataFrame
  |
  +--> source CRS / geometry / properties
  |
  v
CRS service
  |
  +--> geographic CRS -> local UTM projection
  |
  v
Measurement service
  |
  +--> Polygon -> area (m²)
  +--> LineString -> length (m)
  +--> Point -> no measurement
  |
  v
Typed JSON response
```

## Project Structure

```text
geospatial-measurement-api/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── routes.py
│   ├── models/
│   │   └── schemas.py
│   └── services/
│       ├── crs.py
│       ├── file_processor.py
│       └── measurement.py
├── tests/
│   ├── test_api.py
│   ├── test_crs.py
│   └── test_measurement.py
├── uploads/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run Locally

```bash
uvicorn app.main:app --reload
```

Open:

- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health: http://127.0.0.1:8000/health

## API

### `POST /api/files/`

Upload a `.kml` file or `.zip` containing a Shapefile.

```bash
curl -X POST http://127.0.0.1:8000/api/files/ \
  -F "file=@survey.kml"
```

Response:

```json
{
  "id": "abc123",
  "filename": "survey.kml",
  "feature_count": 3,
  "crs": "EPSG:4326",
  "status": "COMPLETED"
}
```

### `GET /api/files/{id}/`

Returns metadata for an uploaded file.

### `GET /api/files/{id}/measurements/`

Returns every feature with:

- feature ID
- geometry type
- original geometry
- source CRS
- properties
- measurement

Example:

```json
{
  "file_id": "abc123",
  "features": [
    {
      "feature_id": 1,
      "geometry_type": "Polygon",
      "geometry": {
        "type": "Polygon",
        "coordinates": []
      },
      "crs": "EPSG:4326",
      "properties": {
        "Name": "Survey Area"
      },
      "measurement": {
        "area": 12016.978112,
        "unit": "m²"
      }
    }
  ]
}
```

## CRS Handling

The service never calculates area or length directly from longitude/latitude degrees.

For geographic CRS such as `EPSG:4326`:

```text
EPSG:4326
    |
    v
estimate local UTM CRS
    |
    v
transform geometry
    |
    v
calculate measurement
```

For already-projected input, the existing projected CRS is retained.

This means polygon measurements are returned in square metres and line measurements in metres.

## Supported Geometry Types

| Geometry | Measurement |
|---|---|
| Point | None |
| Polygon | Area |
| MultiPolygon | Area |
| LineString | Length |
| MultiLineString | Length |
| Other | Graceful unsupported result |

## Validation and Security

- Only `.kml` and `.zip` uploads are accepted.
- Uploads are limited to 50 MB.
- Empty files are rejected.
- ZIP archives are checked for path traversal.
- ZIP archives must contain `.shp`, `.shx`, and `.dbf`.
- CRS information is required for accurate measurements.
- Invalid geospatial data returns a controlled API error.

## Testing

Run:

```bash
pytest
```

The test suite covers:

- health endpoint
- root endpoint
- KML upload
- file information
- measurement endpoint
- polygon area
- LineString length
- point handling
- geographic CRS transformation
- projected CRS preservation
- invalid extensions
- empty uploads
- missing files

## Docker

Build and run:

```bash
docker build -t geospatial-measurement-api .
docker run -p 8000:8000 geospatial-measurement-api
```

Or use Docker Compose:

```bash
docker compose up --build
```

## Design Decisions

### FastAPI

Chosen for its clean routing model, validation, async upload support, and automatic OpenAPI documentation.

### GeoPandas

Used for reading KML/Shapefile data and managing CRS-aware GeoDataFrames.

### Shapely

Used for geometry types and measurement operations.

### Automatic UTM projection

A fixed projected CRS would not be appropriate for files from arbitrary geographic locations. GeoPandas' UTM estimation provides a practical local projection for geographic datasets.

### In-memory metadata

The assignment does not require persistent storage, so metadata is currently held in memory. Restarting the application clears metadata. A production deployment should replace this with PostgreSQL/PostGIS and object storage.

### Synchronous processing

Processing is synchronous because the assignment focuses on API design and measurement logic. Large production workloads should move processing to background workers.

## Learning

This project provided practical experience with:

- REST API design
- multipart file uploads
- geospatial file formats
- GeoPandas
- Shapely
- coordinate reference systems
- projected coordinate systems
- spatial measurements
- ZIP archive security
- validation
- automated testing
- Docker

## Future Scope

- PostgreSQL/PostGIS persistence
- S3-compatible object storage
- Background processing with Celery/RQ
- Authentication and authorization
- Rate limiting
- GeoJSON support
- Additional units such as km, hectares and acres
- Spatial indexing
- Advanced CRS strategies for very large datasets
- Structured logging and monitoring
- Pagination for very large feature collections
- CI/CD with GitHub Actions
