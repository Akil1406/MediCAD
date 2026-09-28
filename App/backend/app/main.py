"""MediCAD FastAPI Application Entrypoint."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import datetime

from .config import (
    APP_NAME, APP_VERSION, API_PREFIX,
    CORS_ORIGINS, MEDICAL_DEVICE_DISCLAIMER
)
from .api.routes import designs, cad, materials, simulations, exports, ai


app = FastAPI(
    title=f"{APP_NAME} Engineering API",
    version=APP_VERSION,
    description="Parametric Medical Tool CAD Prototyping & Analysis REST API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler for cleaner frontend error parsing
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(exc),
                "path": str(request.url.path)
            }
        }
    )

# Register API routes
app.include_router(designs.router, prefix=API_PREFIX)
app.include_router(cad.router, prefix=API_PREFIX)
app.include_router(materials.router, prefix=API_PREFIX)
app.include_router(simulations.router, prefix=API_PREFIX)
app.include_router(exports.router, prefix=API_PREFIX)
app.include_router(ai.router, prefix=API_PREFIX)


@app.get("/health", tags=["System"])
def health_check():
    """System health check and safety boundary status."""
    return {
        "status": "HEALTHY",
        "app_name": APP_NAME,
        "version": APP_VERSION,
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "disclaimer": MEDICAL_DEVICE_DISCLAIMER
    }


@app.get("/", tags=["System"])
def root():
    return {
        "message": f"Welcome to {APP_NAME} v{APP_VERSION} REST API",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
