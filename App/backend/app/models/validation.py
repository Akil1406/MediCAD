"""Validation reports, issues, and severity classifications."""

from pydantic import BaseModel, Field
from typing import Literal
from enum import Enum


class SeverityLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    BLOCKED = "BLOCKED"


class ValidationIssue(BaseModel):
    severity: SeverityLevel
    code: str
    message: str
    parameter: str | None = None
    suggested_fix: str | None = None
    measured_value: float | None = None
    threshold_value: float | None = None


class ValidationReport(BaseModel):
    passed: bool
    device_type: str
    solid_valid: bool = True
    wall_thickness_mm: float | None = None
    total_volume_mm3: float | None = None
    total_surface_area_mm2: float | None = None
    aspect_ratio: float | None = None
    issues: list[ValidationIssue] = Field(default_factory=list)
    timestamp: str | None = None

    @property
    def has_errors(self) -> bool:
        return any(i.severity in (SeverityLevel.ERROR, SeverityLevel.BLOCKED) for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == SeverityLevel.WARNING for i in self.issues)

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity in (SeverityLevel.ERROR, SeverityLevel.BLOCKED))

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == SeverityLevel.WARNING)
