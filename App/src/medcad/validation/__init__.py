"""MediCAD Validation Package."""

from .geometry import validate_geometric_spec
from .design_rules import evaluate_manufacturing_rules
from ..models.base import BaseSpec
from ..models.validation import ValidationReport
from ..cad.base import CADResult


def run_full_validation(
    spec: BaseSpec,
    cad_result: CADResult | None = None,
    manufacturing_process: str | None = None
) -> ValidationReport:
    """Execute Level 1 and Level 2 validation checks in unified pipeline."""
    report = validate_geometric_spec(spec, cad_result)
    if manufacturing_process:
        mfg_issues = evaluate_manufacturing_rules(spec, manufacturing_process)
        report.issues.extend(mfg_issues)
        report.passed = not report.has_errors
    return report


__all__ = [
    "validate_geometric_spec",
    "evaluate_manufacturing_rules",
    "run_full_validation",
]
