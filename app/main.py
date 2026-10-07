from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="Geospatial File Measurement API",
    version="1.0.0",
    description="Upload KML or zipped Shapefiles and calculate spatial measurements.",
)

app.include_router(router, prefix="/api")


@app.get("/", tags=["health"])
def root():
    return {
        "name": "Geospatial File Measurement API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "ok",
    }


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}