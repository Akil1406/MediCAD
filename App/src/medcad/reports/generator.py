"""Engineering specification and validation report generator."""

import datetime
from ..models.base import BaseSpec
from ..models.validation import ValidationReport
from ..models.materials import CandidateScore
from ..cad.base import CADResult
from ..config import APP_NAME, APP_VERSION, MEDICAL_DEVICE_DISCLAIMER


def generate_engineering_report(
    design_id: str,
    version: int,
    spec: BaseSpec,
    cad_result: CADResult,
    validation_report: ValidationReport,
    material_candidates: list[CandidateScore] | None = None,
    simulation_results: list[dict] | None = None,
    user_prompt: str = ""
) -> str:
    """Generate comprehensive Markdown engineering design and verification report."""
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        f"# {APP_NAME} Engineering Prototyping Report",
        f"**Design Identifier:** `{design_id}` | **Version:** `v{version}`",
        f"**Generated:** {now} | **Application:** `{APP_NAME} v{APP_VERSION}`",
        "",
        "> [!IMPORTANT]",
        f"> **Safety & Regulatory Notice:** {MEDICAL_DEVICE_DISCLAIMER}",
        "",
        "## 1. Design Intent & Specification",
        f"- **Device Type:** `{spec.device_type}`",
        f"- **Units:** `{spec.units}`",
        f"- **Tolerance:** `±{spec.tolerance_mm} mm`",
    ]

    if user_prompt:
        lines.append(f"- **Intake Request:** *\"{user_prompt}\"*")

    lines.extend([
        "",
        "### Input Parameters",
        "| Parameter | Value | Units |",
        "|---|---|---|"
    ])

    for k, v in spec.model_dump().items():
        if k not in ("device_type", "units", "notes"):
            lines.append(f"| `{k}` | `{v}` | mm / deg |")

    lines.extend([
        "",
        "### Derived CAD Geometry Properties",
        f"- **Solid Mesh Watertight:** `{'✓ Pass' if cad_result.is_watertight else '✗ Fail'}`",
        f"- **Calculated Volume:** `{cad_result.volume_mm3:.2f} mm³`",
        f"- **Surface Area:** `{cad_result.surface_area_mm2:.2f} mm²`",
        f"- **Bounding Box:** `[{cad_result.bounding_box.size_x:.2f} x {cad_result.bounding_box.size_y:.2f} x {cad_result.bounding_box.size_z:.2f}] mm`",
    ])

    for k, v in cad_result.derived_parameters.items():
        if isinstance(v, float):
            lines.append(f"- **{k.replace('_', ' ').title()}:** `{v:.3f}`")
        elif isinstance(v, (int, str, bool)):
            lines.append(f"- **{k.replace('_', ' ').title()}:** `{v}`")

    lines.extend([
        "",
        "## 2. Engineering & Geometric Validation",
        f"**Overall Status:** `{'✓ PASSED' if validation_report.passed else '⚠ ISSUES DETECTED'}`",
        f"- Errors: `{validation_report.error_count}` | Warnings: `{validation_report.warning_count}`",
        ""
    ])

    if validation_report.issues:
        lines.extend([
            "| Severity | Rule Code | Message | Parameter | Suggested Action |",
            "|---|---|---|---|---|"
        ])
        for issue in validation_report.issues:
            lines.append(
                f"| **{issue.severity.value}** | `{issue.code}` | {issue.message} | `{issue.parameter or 'N/A'}` | {issue.suggested_fix or 'Review design'} |"
            )
    else:
        lines.append("✓ All Level 1 geometric checks and Level 2 manufacturing constraints passed with zero warnings.")

    if material_candidates:
        lines.extend([
            "",
            "## 3. Candidate Medical Materials Evaluation",
            "| Rank | Material Name | Fit Tier | Score | Tensile Strength | Modulus | Sterilization |",
            "|---|---|---|---|---|---|---|"
        ])
        for idx, cand in enumerate(material_candidates[:5], 1):
            m = cand.material
            lines.append(
                f"| #{idx} | **{m.name}** | `{cand.engineering_fit}` | `{cand.score:.2f}` | `{m.tensile_strength_mpa:.1f} MPa` | `{m.elastic_modulus_mpa:.0f} MPa` | {m.sterilization_compatibility.get('EtO', 'Compatible')} |"
            )

    if simulation_results:
        lines.extend([
            "",
            "## 4. Deterministic Engineering Simulation Summary",
            ""
        ])
        for sim in simulation_results:
            sim_type = sim.get("simulation_type", "Simulation").replace("_", " ").title()
            lines.append(f"### {sim_type}")
            for sk, sv in sim.items():
                if sk not in ("simulation_type", "assumptions"):
                    lines.append(f"- **{sk.replace('_', ' ').title()}:** `{sv}`")

    lines.extend([
        "",
        "## 5. Traceability & Export Artifacts",
        f"- **STEP CAD Model:** `{cad_result.device_type}_v{version}.step` (Authoritative B-Rep)",
        f"- **STL Mesh Preview:** `{cad_result.device_type}_v{version}.stl` (Visualization)",
        f"- **Design Specification:** `{cad_result.device_type}_v{version}_spec.json`",
        "",
        "---",
        "*Confidential — MediCAD Parametric Prototyping System*"
    ])

    return "\n".join(lines)
