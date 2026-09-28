"""FastAPI routes for design creation, retrieval, and parameter updates."""

from fastapi import APIRouter, HTTPException, status
import json
import uuid

from ...models.specs import (
    TubeSpec, CatheterSpec, TaperedTubeSpec,
    ConnectorSpec, InjectorSpec, PlungerSpec, AssemblySpec,
    DesignCreateRequest, ParameterUpdateRequest
)
from ...cad import CAD_BUILDERS, export_design_package
from ...validation import run_full_validation
from ...materials import evaluate_and_rank_materials, MaterialDatabase
from ...models.materials import MaterialRequirements
from ...storage import DesignStorage, VersionComparator
from ...agents import run_design_pipeline

router = APIRouter(prefix="/designs", tags=["Designs"])
storage = DesignStorage()
db = MaterialDatabase()

SPEC_CLASSES = {
    "tube": TubeSpec,
    "catheter": CatheterSpec,
    "tapered_tube": TaperedTubeSpec,
    "connector": ConnectorSpec,
    "injector": InjectorSpec,
    "plunger": PlungerSpec,
}

DEFAULT_SPECS = {
    "tube": {"device_type": "tube", "length_mm": 100.0, "outer_diameter_mm": 3.0, "inner_diameter_mm": 2.0},
    "catheter": {"device_type": "catheter", "length_mm": 150.0, "outer_diameter_mm": 2.0, "inner_diameter_mm": 1.2, "tip_length_mm": 5.0, "tip_angle_deg": 0.0, "has_luer_hub": True},
    "tapered_tube": {"device_type": "tapered_tube", "length_mm": 120.0, "proximal_outer_diameter_mm": 4.0, "distal_outer_diameter_mm": 2.0, "inner_diameter_mm": 1.2},
    "connector": {"device_type": "connector", "connector_type": "male_luer", "length_mm": 20.0, "outer_diameter_mm": 6.5, "inner_diameter_mm": 2.5, "barb_count": 2},
    "injector": {"device_type": "injector", "body_length_mm": 80.0, "body_outer_diameter_mm": 16.0, "body_inner_diameter_mm": 14.0, "nozzle_length_mm": 10.0, "nozzle_outer_diameter_mm": 4.0, "nozzle_inner_diameter_mm": 1.8, "flange_width_mm": 24.0, "flange_thickness_mm": 2.5},
    "plunger": {"device_type": "plunger", "plunger_length_mm": 90.0, "rod_diameter_mm": 6.0, "head_outer_diameter_mm": 13.9, "head_length_mm": 8.0, "thumb_rest_diameter_mm": 18.0, "thumb_rest_thickness_mm": 2.0},
}


@router.get("")
def list_all_designs():
    """List all design projects with latest version info."""
    return {"designs": storage.list_designs()}


@router.post("", status_code=status.HTTP_201_CREATED)
def create_design(payload: DesignCreateRequest):
    """Create a new design via AI intent prompt or manual template specification."""
    design_id = f"DES_{payload.device_type.upper()}_{uuid.uuid4().hex[:6].upper()}"

    if payload.prompt:
        # Run agentic extraction pipeline
        pipeline_res = run_design_pipeline(payload.prompt)
        spec_dict = pipeline_res["specification"]
        device_type = spec_dict.get("device_type", payload.device_type)
        user_prompt = payload.prompt
    else:
        device_type = payload.device_type
        if device_type not in SPEC_CLASSES:
            raise HTTPException(status_code=400, detail=f"Unsupported device type: {device_type}")
        base_spec = dict(DEFAULT_SPECS.get(device_type, {}))
        base_spec.update(payload.dimensions)
        spec_dict = base_spec
        user_prompt = "Manual template initialization"

    # Validate specification with Pydantic
    spec_cls = SPEC_CLASSES[device_type]
    try:
        spec_obj = spec_cls(**spec_dict)
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail={"code": "INVALID_SPECIFICATION", "message": str(e)}
        )

    # Build CAD
    builder = CAD_BUILDERS[device_type]
    mesh, cad_res = builder(spec_obj)

    # Run Validation
    val_report = run_full_validation(spec_obj, cad_res)

    # Evaluate Materials
    reqs = MaterialRequirements(
        flexibility_preference="flexible" if device_type == "catheter" else "any"
    )
    ranked_mats = evaluate_and_rank_materials(reqs, db=db)
    mats_data = [m.model_dump() for m in ranked_mats[:5]]

    # Generate initial export package
    bundle_paths = export_design_package(
        mesh=mesh,
        cad_result=cad_res,
        spec_dict=spec_obj.model_dump(),
        validation_dict=val_report.model_dump(),
        design_id=design_id,
        version=1
    )

    # Save to SQLite storage
    v_num = storage.save_design_version(
        design_id=design_id,
        title=payload.title,
        device_type=device_type,
        specification=spec_obj.model_dump(),
        cad_properties=cad_res.model_dump(),
        validation_report=val_report.model_dump(),
        user_prompt=user_prompt,
        material_candidates=mats_data,
        export_paths=bundle_paths
    )

    return {
        "design_id": design_id,
        "version": v_num,
        "title": payload.title,
        "device_type": device_type,
        "specification": spec_obj.model_dump(),
        "cad_properties": cad_res.model_dump(),
        "validation": val_report.model_dump(),
        "material_candidates": mats_data,
        "export_paths": bundle_paths,
        "mesh_stl_bytes": base64_stl_preview(mesh)
    }


@router.get("/{design_id}")
def get_design_details(design_id: str):
    """Fetch current design with its version history."""
    design = storage.get_design(design_id)
    if not design:
        raise HTTPException(status_code=404, detail=f"Design '{design_id}' not found.")

    history = storage.get_design_history(design_id)
    latest = storage.get_latest_version(design_id)

    # Parse JSON strings in latest version
    latest_parsed = dict(latest) if latest else {}
    for key in ("specification_json", "cad_properties_json", "validation_json", "material_candidates_json", "export_paths_json"):
        if key in latest_parsed and isinstance(latest_parsed[key], str):
            latest_parsed[key] = json.loads(latest_parsed[key])

    return {
        "design": design,
        "latest_version": latest_parsed,
        "history": history
    }


@router.patch("/{design_id}/parameters")
def update_design_parameters(design_id: str, payload: ParameterUpdateRequest):
    """Update dimensions: validates input, creates new immutable version, regenerates CAD & validation."""
    design = storage.get_design(design_id)
    if not design:
        raise HTTPException(status_code=404, detail=f"Design '{design_id}' not found.")

    latest = storage.get_latest_version(design_id)
    cur_spec = json.loads(latest["specification_json"]) if isinstance(latest["specification_json"], str) else latest["specification_json"]
    cur_spec.update(payload.parameters)

    device_type = design["device_type"]
    if device_type not in SPEC_CLASSES:
        raise HTTPException(status_code=400, detail=f"Unsupported device type: {device_type}")

    spec_cls = SPEC_CLASSES[device_type]
    try:
        spec_obj = spec_cls(**cur_spec)
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail={"code": "INVALID_PARAMETER", "message": str(e)}
        )

    # Deterministic CAD rebuild
    builder = CAD_BUILDERS[device_type]
    mesh, cad_res = builder(spec_obj)

    # Validation
    val_report = run_full_validation(spec_obj, cad_res)

    # Materials
    reqs = MaterialRequirements(
        flexibility_preference="flexible" if device_type == "catheter" else "any"
    )
    ranked_mats = evaluate_and_rank_materials(reqs, db=db)
    mats_data = [m.model_dump() for m in ranked_mats[:5]]

    # Next version number
    next_ver = design["latest_version"] + 1

    # Export bundle for this version
    bundle_paths = export_design_package(
        mesh=mesh,
        cad_result=cad_res,
        spec_dict=spec_obj.model_dump(),
        validation_dict=val_report.model_dump(),
        design_id=design_id,
        version=next_ver
    )

    v_num = storage.save_design_version(
        design_id=design_id,
        title=design["title"],
        device_type=device_type,
        specification=spec_obj.model_dump(),
        cad_properties=cad_res.model_dump(),
        validation_report=val_report.model_dump(),
        user_prompt=payload.prompt,
        material_candidates=mats_data,
        export_paths=bundle_paths
    )

    return {
        "design_id": design_id,
        "version": v_num,
        "device_type": device_type,
        "specification": spec_obj.model_dump(),
        "cad_properties": cad_res.model_dump(),
        "validation": val_report.model_dump(),
        "material_candidates": mats_data,
        "export_paths": bundle_paths,
        "mesh_stl_bytes": base64_stl_preview(mesh)
    }


@router.get("/{design_id}/validation")
def get_design_validation(design_id: str):
    """Fetch real-time validation report for design."""
    latest = storage.get_latest_version(design_id)
    if not latest:
        raise HTTPException(status_code=404, detail="Design version not found.")

    val_data = json.loads(latest["validation_json"]) if isinstance(latest["validation_json"], str) else latest["validation_json"]
    return {"design_id": design_id, "validation": val_data}


@router.get("/{design_id}/materials")
def get_design_materials(design_id: str):
    """Fetch ranked candidate materials for design."""
    latest = storage.get_latest_version(design_id)
    if not latest:
        raise HTTPException(status_code=404, detail="Design version not found.")

    mats_data = json.loads(latest["material_candidates_json"]) if isinstance(latest["material_candidates_json"], str) else latest["material_candidates_json"]
    return {"design_id": design_id, "candidates": mats_data}


def base64_stl_preview(mesh) -> str:
    import base64
    return base64.b64encode(mesh.to_stl_bytes()).decode("utf-8")
