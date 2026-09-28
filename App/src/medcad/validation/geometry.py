"""Level 1 geometric validation rules."""

import datetime
from ..models.base import BaseSpec
from ..models.specs import (
    TubeSpec,
    CatheterSpec,
    TaperedTubeSpec,
    ConnectorSpec,
    InjectorSpec,
    PlungerSpec
)
from ..models.validation import ValidationIssue, ValidationReport, SeverityLevel
from ..cad.base import SolidMesh, CADResult
from ..config import MIN_WALL_THICKNESS_EXTRUSION_MM, MAX_ASPECT_RATIO_BUCKLING_THRESHOLD


def validate_geometric_spec(spec: BaseSpec, cad_result: CADResult | None = None) -> ValidationReport:
    """Perform deterministic geometric integrity and boundary checks."""
    issues: list[ValidationIssue] = []
    wall_thickness: float | None = None
    aspect_ratio: float | None = None

    if isinstance(spec, TubeSpec):
        wall_thickness = spec.wall_thickness_mm
        aspect_ratio = spec.length_mm / spec.outer_diameter_mm

        if wall_thickness < MIN_WALL_THICKNESS_EXTRUSION_MM:
            issues.append(
                ValidationIssue(
                    severity=SeverityLevel.ERROR,
                    code="GEO_WALL_TOO_THIN",
                    message=f"Wall thickness ({wall_thickness:.3f} mm) is below standard extrusion limit ({MIN_WALL_THICKNESS_EXTRUSION_MM} mm).",
                    parameter="outer_diameter_mm",
                    suggested_fix="Increase outer diameter or reduce inner diameter.",
                    measured_value=wall_thickness,
                    threshold_value=MIN_WALL_THICKNESS_EXTRUSION_MM
                )
            )

        if aspect_ratio > MAX_ASPECT_RATIO_BUCKLING_THRESHOLD:
            issues.append(
                ValidationIssue(
                    severity=SeverityLevel.WARNING,
                    code="GEO_HIGH_ASPECT_RATIO",
                    message=f"High length-to-diameter aspect ratio ({aspect_ratio:.1f}). Column may be prone to flexural buckling during axial insertion.",
                    parameter="length_mm",
                    suggested_fix="Review catheter guide wire support or consider braided reinforcement.",
                    measured_value=aspect_ratio,
                    threshold_value=MAX_ASPECT_RATIO_BUCKLING_THRESHOLD
                )
            )

    elif isinstance(spec, CatheterSpec):
        wall_thickness = spec.shaft_wall_thickness_mm
        aspect_ratio = spec.length_mm / spec.outer_diameter_mm

        if wall_thickness < MIN_WALL_THICKNESS_EXTRUSION_MM:
            issues.append(
                ValidationIssue(
                    severity=SeverityLevel.ERROR,
                    code="GEO_CATH_WALL_THIN",
                    message=f"Catheter shaft wall ({wall_thickness:.3f} mm) is below safe extrusion limit ({MIN_WALL_THICKNESS_EXTRUSION_MM} mm).",
                    parameter="outer_diameter_mm",
                    measured_value=wall_thickness,
                    threshold_value=MIN_WALL_THICKNESS_EXTRUSION_MM
                )
            )

        if spec.tip_length_mm > spec.length_mm * 0.3:
            issues.append(
                ValidationIssue(
                    severity=SeverityLevel.WARNING,
                    code="GEO_TIP_PROPORTION",
                    message=f"Tip length ({spec.tip_length_mm} mm) exceeds 30% of total working length.",
                    parameter="tip_length_mm"
                )
            )

    elif isinstance(spec, TaperedTubeSpec):
        wall_thickness = spec.min_wall_thickness_mm
        if wall_thickness < MIN_WALL_THICKNESS_EXTRUSION_MM:
            issues.append(
                ValidationIssue(
                    severity=SeverityLevel.ERROR,
                    code="GEO_TAPER_MIN_WALL",
                    message=f"Minimum wall thickness at narrow end ({wall_thickness:.3f} mm) is below {MIN_WALL_THICKNESS_EXTRUSION_MM} mm.",
                    parameter="distal_outer_diameter_mm",
                    measured_value=wall_thickness,
                    threshold_value=MIN_WALL_THICKNESS_EXTRUSION_MM
                )
            )

    elif isinstance(spec, InjectorSpec):
        wall_thickness = spec.barrel_wall_thickness_mm
        if wall_thickness < 0.35:
            issues.append(
                ValidationIssue(
                    severity=SeverityLevel.WARNING,
                    code="GEO_BARREL_WALL_THIN",
                    message=f"Syringe barrel wall thickness ({wall_thickness:.2f} mm) may deflect under high hydraulic pressure.",
                    parameter="body_outer_diameter_mm",
                    measured_value=wall_thickness,
                    threshold_value=0.35
                )
            )

    elif isinstance(spec, PlungerSpec):
        if spec.rod_diameter_mm < 1.5:
            issues.append(
                ValidationIssue(
                    severity=SeverityLevel.WARNING,
                    code="GEO_PLUNGER_ROD_SLENDER",
                    message=f"Plunger rod diameter ({spec.rod_diameter_mm} mm) may buckle under heavy manual thumb depression.",
                    parameter="rod_diameter_mm",
                    measured_value=spec.rod_diameter_mm,
                    threshold_value=1.5
                )
            )

    solid_valid = True
    total_vol = cad_result.volume_mm3 if cad_result else None
    total_area = cad_result.surface_area_mm2 if cad_result else None

    if cad_result:
        if not cad_result.is_watertight:
            issues.append(
                ValidationIssue(
                    severity=SeverityLevel.ERROR,
                    code="CAD_MESH_NON_WATERTIGHT",
                    message="Generated solid mesh contains non-manifold or open boundaries."
                )
            )
            solid_valid = False

        if cad_result.volume_mm3 <= 0:
            issues.append(
                ValidationIssue(
                    severity=SeverityLevel.ERROR,
                    code="CAD_VOLUME_ZERO",
                    message="Calculated solid volume is zero or negative."
                )
            )
            solid_valid = False

    passed = not any(i.severity in (SeverityLevel.ERROR, SeverityLevel.BLOCKED) for i in issues)

    return ValidationReport(
        passed=passed,
        device_type=spec.device_type,
        solid_valid=solid_valid,
        wall_thickness_mm=wall_thickness,
        total_volume_mm3=total_vol,
        total_surface_area_mm2=total_area,
        aspect_ratio=aspect_ratio,
        issues=issues,
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
