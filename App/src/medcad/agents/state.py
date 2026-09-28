"""State definition for the LangGraph design workflow."""

from typing import TypedDict, Any


class DesignState(TypedDict, total=False):
    """Workflow state for orchestrating parametric medical CAD design."""
    user_request: str
    target_device_type: str
    specification: dict[str, Any]
    cad_result: dict[str, Any]
    geometry_checks: dict[str, Any]
    material_candidates: list[dict[str, Any]]
    engineering_report: str
    status: str
    errors: list[str]
    revision_count: int
    human_approved: bool
    export_manifest: dict[str, Any]
