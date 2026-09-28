"""Global configuration and paths for MediCAD."""

from pathlib import Path
import os

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
EXPORTS_DIR = PROJECT_ROOT / "exports"
SEED_DATA_PATH = DATA_DIR / "materials_seed.json"
DEFAULT_DB_PATH = DATA_DIR / "medcad.db"

# Ensure runtime directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Application metadata
APP_NAME = "MediCAD"
APP_VERSION = "0.1.0"
AUTHORITATIVE_CAD_FORMAT = "STEP"
PREVIEW_FORMAT = "STL"

# Engineering defaults
DEFAULT_UNITS = "mm"
MIN_WALL_THICKNESS_EXTRUSION_MM = 0.10
MIN_WALL_THICKNESS_MOLDING_MM = 0.40
MIN_WALL_THICKNESS_3DPRINT_MM = 0.30
MAX_ASPECT_RATIO_BUCKLING_THRESHOLD = 50.0

# Safety boundary notice
MEDICAL_DEVICE_DISCLAIMER = (
    "NOTICE: MediCAD generates engineering design prototypes and preliminary analysis artifacts. "
    "Outputs are not clinical advice and are not evidence of safety, efficacy, biocompatibility, "
    "sterilization validation, regulatory approval, or suitability for human use."
)
