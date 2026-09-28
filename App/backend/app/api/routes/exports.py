"""FastAPI routes for controlled CAD artifacts downloads."""

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
from pathlib import Path
import json

from ...config import EXPORTS_DIR
from ...storage import DesignStorage
from ...reports import generate_engineering_report
from ...models.specs import (
    TubeSpec, CatheterSpec, TaperedTubeSpec,
    ConnectorSpec, InjectorSpec, PlungerSpec
)
from ...cad.base import CADResult
from ...models.validation import ValidationReport
from ...models.materials import CandidateScore


router = APIRouter(prefix="/exports", tags=["Exports"])
storage = DesignStorage()

SPEC_CLASSES = {
    "tube": TubeSpec,
    "catheter": CatheterSpec,
    "tapered_tube": TaperedTubeSpec,
    "connector": ConnectorSpec,
    "injector": InjectorSpec,
    "plunger": PlungerSpec,
}


@router.get("/{design_id}/{version}")
def get_export_manifest(design_id: str, version: int):
    """Retrieve metadata manifest for design export version."""
    target_dir = EXPORTS_DIR / f"{design_id}_v{version}"
    manifest_file = target_dir / "manifest.json"
    if not manifest_file.exists():
        raise HTTPException(status_code=404, detail=f"Export package not found for {design_id} v{version}")
    return json.loads(manifest_file.read_text(encoding="utf-8"))


@router.get("/{design_id}/{version}/step")
def download_step_file(design_id: str, version: int):
    """Download authoritative ISO 10303-21 STEP CAD model."""
    target_dir = EXPORTS_DIR / f"{design_id}_v{version}"
    step_files = list(target_dir.glob("*.step"))
    if not step_files:
        raise HTTPException(status_code=404, detail="STEP file not generated for this version.")
    return FileResponse(
        path=step_files[0],
        filename=step_files[0].name,
        media_type="application/step"
    )


@router.get("/{design_id}/{version}/stl")
def download_stl_file(design_id: str, version: int):
    """Download STL triangulated mesh preview."""
    target_dir = EXPORTS_DIR / f"{design_id}_v{version}"
    stl_files = list(target_dir.glob("*.stl"))
    if not stl_files:
        raise HTTPException(status_code=404, detail="STL file not generated for this version.")
    return FileResponse(
        path=stl_files[0],
        filename=stl_files[0].name,
        media_type="application/sla"
    )


@router.get("/{design_id}/{version}/preview")
def get_mesh_preview_stream(design_id: str, version: int):
    """Stream raw STL mesh for 3D viewer."""
    target_dir = EXPORTS_DIR / f"{design_id}_v{version}"
    stl_files = list(target_dir.glob("*.stl"))
    if not stl_files:
        raise HTTPException(status_code=404, detail="Mesh preview not available.")
    return Response(content=stl_files[0].read_bytes(), media_type="application/sla")


@router.get("/{design_id}/{version}/report")
def download_engineering_report(design_id: str, version: int):
    """Download full Markdown engineering prototyping report."""
    history = storage.get_design_history(design_id)
    v_record = next((h for h in history if h["version_number"] == version), None)
    if not v_record:
        raise HTTPException(status_code=404, detail="Version not found.")

    dtype = v_record["device_type"]
    spec_data = json.loads(v_record["specification_json"]) if isinstance(v_record["specification_json"], str) else v_record["specification_json"]
    cad_data = json.loads(v_record["cad_properties_json"]) if isinstance(v_record["cad_properties_json"], str) else v_record["cad_properties_json"]
    val_data = json.loads(v_record["validation_json"]) if isinstance(v_record["validation_json"], str) else v_record["validation_json"]
    mats_data = json.loads(v_record["material_candidates_json"]) if isinstance(v_record["material_candidates_json"], str) else v_record["material_candidates_json"]

    spec_cls = SPEC_CLASSES.get(dtype, TubeSpec)
    spec_obj = spec_cls(**spec_data)
    cad_res = CADResult(**cad_data)
    val_rep = ValidationReport(**val_data)
    cand_objs = [CandidateScore(**c) for c in mats_data]

    report_content = generate_engineering_report(
        design_id=design_id,
        version=version,
        spec=spec_obj,
        cad_result=cad_res,
        validation_report=val_rep,
        material_candidates=cand_objs,
        user_prompt=v_record.get("user_prompt", "")
    )

    return Response(
        content=report_content,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename={design_id}_v{version}_report.md"}
    )
