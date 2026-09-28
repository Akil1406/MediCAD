"""LangChain tool definitions for deterministic CAD, validation, and materials."""

import json
from langchain_core.tools import tool
from ..models.specs import (
    TubeSpec, CatheterSpec, TaperedTubeSpec,
    ConnectorSpec, InjectorSpec, PlungerSpec
)
from ..models.materials import MaterialRequirements
from ..cad import CAD_BUILDERS, build_tube, build_catheter, build_tapered_tube, build_connector, build_injector, build_plunger
from ..validation import run_full_validation
from ..materials import MaterialDatabase, evaluate_and_rank_materials


SPEC_CLASSES = {
    "tube": TubeSpec,
    "catheter": CatheterSpec,
    "tapered_tube": TaperedTubeSpec,
    "connector": ConnectorSpec,
    "injector": InjectorSpec,
    "plunger": PlungerSpec,
}


@tool
def validate_device_spec(spec_json: str) -> str:
    """Validate a JSON device specification against its typed Pydantic schema."""
    try:
        data = json.loads(spec_json)
        dtype = data.get("device_type")
        if dtype not in SPEC_CLASSES:
            return json.dumps({"valid": False, "error": f"Unknown device type: '{dtype}'"})
        spec_obj = SPEC_CLASSES[dtype](**data)
        return json.dumps({"valid": True, "parsed_spec": spec_obj.model_dump()})
    except Exception as e:
        return json.dumps({"valid": False, "error": str(e)})


@tool
def generate_device_cad(device_type: str, spec_json: str) -> str:
    """Generate deterministic 3D solid geometry for a validated parametric device template."""
    try:
        if device_type not in CAD_BUILDERS or device_type not in SPEC_CLASSES:
            return json.dumps({"success": False, "error": f"Unsupported device type '{device_type}'"})

        data = json.loads(spec_json)
        spec_obj = SPEC_CLASSES[device_type](**data)
        builder = CAD_BUILDERS[device_type]
        mesh, cad_res = builder(spec_obj)

        return json.dumps({
            "success": True,
            "device_type": device_type,
            "volume_mm3": cad_res.volume_mm3,
            "surface_area_mm2": cad_res.surface_area_mm2,
            "is_watertight": cad_res.is_watertight,
            "derived_parameters": cad_res.derived_parameters
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def search_materials(requirements_json: str) -> str:
    """Search and score candidate medical materials matching explicit engineering requirements."""
    try:
        data = json.loads(requirements_json)
        reqs = MaterialRequirements(**data)
        db = MaterialDatabase()
        scored = evaluate_and_rank_materials(reqs, db=db)
        results = [
            {
                "material_name": s.material.name,
                "score": s.score,
                "fit": s.engineering_fit,
                "tensile_strength_mpa": s.material.tensile_strength_mpa,
                "modulus_mpa": s.material.elastic_modulus_mpa,
                "matched_criteria": s.matched_criteria,
                "unmatched_criteria": s.unmatched_criteria,
                "source": s.material.source
            }
            for s in scored[:5]
        ]
        return json.dumps({"success": True, "candidates": results})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool
def run_geometry_checks(spec_json: str) -> str:
    """Run deterministic geometric validation and manufacturing rules on specification."""
    try:
        data = json.loads(spec_json)
        dtype = data.get("device_type")
        if dtype not in SPEC_CLASSES:
            return json.dumps({"error": f"Unknown device type: '{dtype}'"})

        spec_obj = SPEC_CLASSES[dtype](**data)
        builder = CAD_BUILDERS[dtype]
        mesh, cad_res = builder(spec_obj)
        report = run_full_validation(spec_obj, cad_res)

        return json.dumps({
            "passed": report.passed,
            "has_errors": report.has_errors,
            "has_warnings": report.has_warnings,
            "wall_thickness_mm": report.wall_thickness_mm,
            "aspect_ratio": report.aspect_ratio,
            "issues": [i.model_dump() for i in report.issues]
        })
    except Exception as e:
        return json.dumps({"error": str(e)})
