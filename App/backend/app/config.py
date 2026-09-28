"""Global configuration for MediCAD FastAPI backend."""

from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
EXPORTS_DIR = PROJECT_ROOT / "exports"
DEFAULT_DB_PATH = DATA_DIR / "medcad.db"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

APP_NAME = "MediCAD"
APP_VERSION = "0.1.0"
API_PREFIX = "/api/v1"

CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"
]

MEDICAL_DEVICE_DISCLAIMER = (
    "NOTICE: MediCAD generates engineering design prototypes and preliminary analysis artifacts. "
    "Outputs are not clinical advice and are not evidence of safety, efficacy, biocompatibility, "
    "sterilization validation, regulatory approval, or suitability for human use."
)
