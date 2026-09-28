"""FastAPI routes for CAD generation and 3D mesh previews."""

from fastapi import APIRouter, HTTPException, Response
import base64
from ...models.specs import (
    TubeSpec, CatheterSpec, TaperedTubeSpec,
    ConnectorSpec, InjectorSpec, PlungerSpec, AssemblySpec
)
from ...cad import CAD_BUILDERS, build_tube, build_catheter, build_tapered_tube, build_connector, build_injector, build_plunger, build_syringe_assembly


router = APIRouter(prefix="/cad", tags=["CAD Engine"])

SPEC_CLASSES = {
    "tube": TubeSpec,
    "catheter": CatheterSpec,
    "tapered_tube": TaperedTubeSpec,
    "connector": ConnectorSpec,
    "injector": InjectorSpec,
    "plunger": PlungerSpec,
    "assembly": AssemblySpec,
}

DEFAULT_SPECS = {
    "tube": TubeSpec(length_mm=100.0, outer_diameter_mm=3.0, inner_diameter_mm=2.0),
    "catheter": CatheterSpec(length_mm=150.0, outer_diameter_mm=2.0, inner_diameter_mm=1.2, tip_length_mm=5.0, tip_angle_deg=0.0, has_luer_hub=True),
    "tapered_tube": TaperedTubeSpec(length_mm=120.0, proximal_outer_diameter_mm=4.0, distal_outer_diameter_mm=2.0, inner_diameter_mm=1.2),
    "connector": ConnectorSpec(length_mm=20.0, outer_diameter_mm=6.5, inner_diameter_mm=2.5, barb_count=2),
    "injector": InjectorSpec(body_length_mm=80.0, body_outer_diameter_mm=16.0, body_inner_diameter_mm=14.0, nozzle_length_mm=10.0, nozzle_outer_diameter_mm=4.0, nozzle_inner_diameter_mm=1.8, flange_width_mm=24.0, flange_thickness_mm=2.5),
    "plunger": PlungerSpec(plunger_length_mm=90.0, rod_diameter_mm=6.0, head_outer_diameter_mm=13.9, head_length_mm=8.0, thumb_rest_diameter_mm=18.0, thumb_rest_thickness_mm=2.0),
}


@router.post("/build")
def build_cad_model(payload: dict):
    """Build deterministic 3D geometry from specification payload."""
    dtype = payload.get("device_type")
    if dtype not in SPEC_CLASSES:
        raise HTTPException(status_code=400, detail=f"Unknown device type: '{dtype}'")

    spec_cls = SPEC_CLASSES[dtype]
    try:
        spec_obj = spec_cls(**payload)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    if dtype == "assembly":
        mesh, cad_res, analysis = build_syringe_assembly(spec_obj)
    else:
        builder = CAD_BUILDERS[dtype]
        mesh, cad_res = builder(spec_obj)

    stl_b64 = base64.b64encode(mesh.to_stl_bytes()).decode("utf-8")

    return {
        "success": True,
        "device_type": dtype,
        "cad_properties": cad_res.model_dump(),
        "stl_base64": stl_b64
    }


@router.get("/preview/{device_type}")
def get_default_cad_preview(device_type: str):
    """Fetch default template preview mesh."""
    if device_type not in DEFAULT_SPECS:
        raise HTTPException(status_code=404, detail=f"Unknown template: '{device_type}'")

    spec = DEFAULT_SPECS[device_type]
    builder = CAD_BUILDERS[device_type]
    mesh, cad_res = builder(spec)

    stl_bytes = mesh.to_stl_bytes()
    return Response(content=stl_bytes, media_type="application/sla")
