from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

KML = b'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
<Placemark><name>Point</name><Point><coordinates>77.5946,12.9716,0</coordinates></Point></Placemark>
<Placemark><name>Polygon</name><Polygon><outerBoundaryIs><LinearRing><coordinates>
77.5946,12.9716,0 77.5956,12.9716,0 77.5956,12.9726,0
77.5946,12.9726,0 77.5946,12.9716,0
</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark>
<Placemark><name>Line</name><LineString><coordinates>
77.5946,12.9716,0 77.5966,12.9736,0
</coordinates></LineString></Placemark>
</Document>
</kml>'''


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_kml_upload_and_measurements():
    response = client.post(
        "/api/files/",
        files={"file": ("test.kml", BytesIO(KML), "application/vnd.google-earth.kml+xml")},
    )
    assert response.status_code == 201

    file_id = response.json()["id"]

    info = client.get(f"/api/files/{file_id}/")
    assert info.status_code == 200
    assert info.json()["feature_count"] == 3

    measurements = client.get(f"/api/files/{file_id}/measurements/")
    assert measurements.status_code == 200

    features = measurements.json()["features"]
    assert features[0]["measurement"] is None
    assert features[1]["measurement"]["unit"] == "m²"
    assert features[1]["measurement"]["area"] > 10000
    assert features[2]["measurement"]["unit"] == "m"


def test_invalid_extension():
    response = client.post(
        "/api/files/",
        files={"file": ("test.txt", BytesIO(b"hello"), "text/plain")},
    )
    assert response.status_code == 400


def test_empty_file():
    response = client.post(
        "/api/files/",
        files={"file": ("empty.kml", BytesIO(b""), "application/xml")},
    )
    assert response.status_code == 400


def test_missing_file():
    response = client.get("/api/files/not-real/")
    assert response.status_code == 404
