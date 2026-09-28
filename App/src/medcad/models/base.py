"""Base models and foundational data types."""

from pydantic import BaseModel, Field
from typing import Literal

UnitType = Literal["mm", "in", "um"]

class BoundingBox(BaseModel):
    """3D Axis-Aligned Bounding Box."""
    min_x: float
    max_x: float
    min_y: float
    max_y: float
    min_z: float
    max_z: float

    @property
    def size_x(self) -> float:
        return self.max_x - self.min_x

    @property
    def size_y(self) -> float:
        return self.max_y - self.min_y

    @property
    def size_z(self) -> float:
        return self.max_z - self.min_z


class BaseSpec(BaseModel):
    """Base specification for all parametric medical devices."""
    device_type: str
    units: UnitType = "mm"
    tolerance_mm: float = Field(default=0.05, gt=0, description="Geometric tolerance in mm")
    notes: str = Field(default="", description="Optional design or manufacturing notes")

    model_config = {
        "extra": "forbid",
        "validate_assignment": True
    }
