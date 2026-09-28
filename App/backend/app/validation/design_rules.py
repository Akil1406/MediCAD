"""Level 2 manufacturing design rules."""

from ..models.base import BaseSpec
from ..models.validation import ValidationIssue, SeverityLevel


def evaluate_manufacturing_rules(spec: BaseSpec, process_type: str = "extrusion") -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    process = process_type.lower()

    if "extrusion" in process:
        if hasattr(spec, "outer_diameter_mm") and hasattr(spec, "inner_diameter_mm"):
            wall = (spec.outer_diameter_mm - spec.inner_diameter_mm) / 2.0
            if wall < 0.08:
                issues.append(
                    ValidationIssue(
                        severity=SeverityLevel.ERROR,
                        code="MFG_EXTRUSION_MIN_WALL",
                        message=f"Wall thickness {wall:.3f} mm violates high-yield precision micro-extrusion limits (<0.08 mm).",
                        parameter="outer_diameter_mm"
                    )
                )

    elif "molding" in process or "injection" in process:
        if hasattr(spec, "wall_thickness_mm"):
            wall = getattr(spec, "wall_thickness_mm")
            if wall < 0.35:
                issues.append(
                    ValidationIssue(
                        severity=SeverityLevel.WARNING,
                        code="MFG_MOLDING_SHORT_SHOT",
                        message=f"Thin section ({wall:.2f} mm) may cause high injection pressure or short shot defects.",
                        parameter="wall_thickness_mm"
                    )
                )

    elif "3d" in process or "additive" in process:
        if hasattr(spec, "inner_diameter_mm"):
            id_val = getattr(spec, "inner_diameter_mm")
            if id_val < 0.5:
                issues.append(
                    ValidationIssue(
                        severity=SeverityLevel.WARNING,
                        code="MFG_AM_MIN_CHANNEL",
                        message=f"Micro-channel ID ({id_val:.2f} mm) risks resin trapping in SLA 3D printing.",
                        parameter="inner_diameter_mm"
                    )
                )

    return issues
