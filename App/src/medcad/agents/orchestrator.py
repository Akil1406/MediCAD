"""LangGraph orchestrator for medical CAD prototyping workflow."""

import re
import json
from typing import Literal
from langgraph.graph import StateGraph, END
from .state import DesignState
from ..models.specs import (
    TubeSpec, CatheterSpec, TaperedTubeSpec,
    ConnectorSpec, InjectorSpec, PlungerSpec
)
from ..cad import CAD_BUILDERS
from ..cad.base import CADResult
from ..models.validation import ValidationReport
from ..models.materials import CandidateScore
from ..validation import run_full_validation
from ..materials import evaluate_and_rank_materials, MaterialDatabase
from ..models.materials import MaterialRequirements
from ..reports import generate_engineering_report


SPEC_MAPPINGS = {
    "tube": TubeSpec,
    "catheter": CatheterSpec,
    "tapered_tube": TaperedTubeSpec,
    "connector": ConnectorSpec,
    "injector": InjectorSpec,
    "plunger": PlungerSpec,
}


def parse_intent_fallback(user_request: str) -> dict:
    """Deterministic natural language parser to extract parameters from text."""
    req_lower = user_request.lower()

    if "catheter" in req_lower:
        device_type = "catheter"
    elif "taper" in req_lower:
        device_type = "tapered_tube"
    elif "connector" in req_lower or "luer" in req_lower:
        device_type = "connector"
    elif "syringe" in req_lower or "injector" in req_lower or "barrel" in req_lower:
        device_type = "injector"
    elif "plunger" in req_lower or "piston" in req_lower:
        device_type = "plunger"
    else:
        device_type = "tube"

    def extract_num(pattern: str, default: float) -> float:
        m = re.search(pattern, user_request, re.IGNORECASE)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                pass
        return default

    if device_type == "catheter":
        length = extract_num(r"(?:length|len|long)[\s:=]*(\d+(?:\.\d+)?)", 150.0)
        od = extract_num(r"(?:od|outer diameter|diameter)[\s:=]*(\d+(?:\.\d+)?)", 2.0)
        id_val = extract_num(r"(?:id|inner diameter|lumen)[\s:=]*(\d+(?:\.\d+)?)", 1.2)
        tip_len = extract_num(r"(?:tip length|tip)[\s:=]*(\d+(?:\.\d+)?)", 5.0)
        tip_ang = extract_num(r"(?:angle|bevel|curve)[\s:=]*(\d+(?:\.\d+)?)", 0.0)
        return {
            "device_type": "catheter",
            "length_mm": length,
            "outer_diameter_mm": od,
            "inner_diameter_mm": min(id_val, od * 0.7),
            "tip_length_mm": tip_len,
            "tip_angle_deg": tip_ang,
            "has_luer_hub": True
        }

    elif device_type == "tube":
        length = extract_num(r"(?:length|len|long)[\s:=]*(\d+(?:\.\d+)?)", 100.0)
        od = extract_num(r"(?:od|outer diameter|diameter)[\s:=]*(\d+(?:\.\d+)?)", 3.0)
        id_val = extract_num(r"(?:id|inner diameter|lumen|bore)[\s:=]*(\d+(?:\.\d+)?)", 2.0)
        return {
            "device_type": "tube",
            "length_mm": length,
            "outer_diameter_mm": od,
            "inner_diameter_mm": min(id_val, od * 0.75)
        }

    elif device_type == "injector":
        b_len = extract_num(r"(?:body|length|barrel)[\s:=]*(\d+(?:\.\d+)?)", 80.0)
        b_od = extract_num(r"(?:body od|outer diameter)[\s:=]*(\d+(?:\.\d+)?)", 16.0)
        b_id = extract_num(r"(?:body id|inner diameter|bore)[\s:=]*(\d+(?:\.\d+)?)", 14.0)
        return {
            "device_type": "injector",
            "body_length_mm": b_len,
            "body_outer_diameter_mm": b_od,
            "body_inner_diameter_mm": b_id,
            "nozzle_length_mm": 10.0,
            "nozzle_outer_diameter_mm": 4.0,
            "nozzle_inner_diameter_mm": 1.8,
            "flange_width_mm": 24.0,
            "flange_thickness_mm": 2.5
        }

    elif device_type == "plunger":
        p_len = extract_num(r"(?:length|plunger)[\s:=]*(\d+(?:\.\d+)?)", 90.0)
        h_od = extract_num(r"(?:head|stopper|diameter)[\s:=]*(\d+(?:\.\d+)?)", 13.9)
        r_od = extract_num(r"(?:rod|shaft)[\s:=]*(\d+(?:\.\d+)?)", 6.0)
        return {
            "device_type": "plunger",
            "plunger_length_mm": p_len,
            "head_outer_diameter_mm": h_od,
            "rod_diameter_mm": r_od,
            "thumb_rest_diameter_mm": 18.0,
            "thumb_rest_thickness_mm": 2.0
        }

    elif device_type == "tapered_tube":
        length = extract_num(r"(?:length|len)[\s:=]*(\d+(?:\.\d+)?)", 120.0)
        prox_od = extract_num(r"(?:proximal|large od)[\s:=]*(\d+(?:\.\d+)?)", 4.0)
        dist_od = extract_num(r"(?:distal|small od|tip od)[\s:=]*(\d+(?:\.\d+)?)", 2.0)
        id_val = extract_num(r"(?:id|inner)[\s:=]*(\d+(?:\.\d+)?)", 1.2)
        return {
            "device_type": "tapered_tube",
            "length_mm": length,
            "proximal_outer_diameter_mm": prox_od,
            "distal_outer_diameter_mm": dist_od,
            "inner_diameter_mm": id_val
        }

    elif device_type == "connector":
        return {
            "device_type": "connector",
            "connector_type": "male_luer",
            "length_mm": 20.0,
            "outer_diameter_mm": 6.5,
            "inner_diameter_mm": 2.5,
            "barb_count": 2
        }

    return {"device_type": "tube", "length_mm": 100.0, "outer_diameter_mm": 3.0, "inner_diameter_mm": 2.0}


# Graph Nodes
def extract_requirements_node(state: DesignState) -> dict:
    """Convert natural-language prompt into structured specification."""
    req_text = state.get("user_request", "")
    spec_data = parse_intent_fallback(req_text)
    return {
        "target_device_type": spec_data["device_type"],
        "specification": spec_data,
        "revision_count": state.get("revision_count", 0),
        "errors": []
    }


def generate_cad_node(state: DesignState) -> dict:
    """Invoke deterministic CAD generator for the validated specification."""
    spec_data = state["specification"]
    dtype = spec_data.get("device_type", "tube")
    spec_cls = SPEC_MAPPINGS[dtype]
    spec_obj = spec_cls(**spec_data)

    builder = CAD_BUILDERS[dtype]
    mesh, cad_res = builder(spec_obj)

    return {
        "cad_result": cad_res.model_dump()
    }


def run_geometry_checks_node(state: DesignState) -> dict:
    """Execute Level 1 geometric checks and Level 2 manufacturing rules."""
    spec_data = state["specification"]
    dtype = spec_data.get("device_type", "tube")
    spec_cls = SPEC_MAPPINGS[dtype]
    spec_obj = spec_cls(**spec_data)

    cad_res_dict = state["cad_result"]
    cad_res = CADResult(**cad_res_dict)

    report = run_full_validation(spec_obj, cad_res)
    errors = [i.message for i in report.issues if i.severity.value in ("ERROR", "BLOCKED")]

    return {
        "geometry_checks": report.model_dump(),
        "errors": errors
    }


def revise_specification_node(state: DesignState) -> dict:
    """Bounded automated parameter correction for geometric conflicts."""
    spec_data = dict(state["specification"])
    cur_revisions = state.get("revision_count", 0) + 1

    # Fix OD <= ID conflicts
    if "outer_diameter_mm" in spec_data and "inner_diameter_mm" in spec_data:
        if spec_data["inner_diameter_mm"] >= spec_data["outer_diameter_mm"]:
            spec_data["inner_diameter_mm"] = spec_data["outer_diameter_mm"] * 0.70

    return {
        "specification": spec_data,
        "revision_count": cur_revisions,
        "errors": []
    }


def evaluate_materials_node(state: DesignState) -> dict:
    """Filter and rank candidate medical materials."""
    db = MaterialDatabase()
    dtype = state.get("target_device_type", "tube")
    flex_target = "flexible" if dtype == "catheter" else ("rigid" if dtype in ("connector", "injector") else "any")

    reqs = MaterialRequirements(
        flexibility_preference=flex_target,
        preferred_manufacturing_method="Extrusion" if dtype in ("tube", "catheter") else "Injection Molding"
    )
    scored = evaluate_and_rank_materials(reqs, db=db)
    candidates_data = [s.model_dump() for s in scored[:5]]

    return {
        "material_candidates": candidates_data
    }


def generate_report_node(state: DesignState) -> dict:
    """Generate comprehensive engineering prototyping report."""
    spec_data = state["specification"]
    dtype = spec_data.get("device_type", "tube")
    spec_cls = SPEC_MAPPINGS[dtype]
    spec_obj = spec_cls(**spec_data)

    cad_res = CADResult(**state["cad_result"])
    val_rep = ValidationReport(**state["geometry_checks"])
    cand_objs = [CandidateScore(**c) for c in state.get("material_candidates", [])]

    report_md = generate_engineering_report(
        design_id="DES_" + state.get("target_device_type", "MED").upper(),
        version=1,
        spec=spec_obj,
        cad_result=cad_res,
        validation_report=val_rep,
        material_candidates=cand_objs,
        user_prompt=state.get("user_request", "")
    )

    return {
        "engineering_report": report_md,
        "status": "COMPLETED"
    }


def should_revise(state: DesignState) -> Literal["revise", "proceed"]:
    """Conditional router for geometric error revision loop."""
    errors = state.get("errors", [])
    rev_count = state.get("revision_count", 0)
    if errors and rev_count < 2:
        return "revise"
    return "proceed"


# Construct the StateGraph workflow
def build_medcad_graph():
    graph = StateGraph(DesignState)

    graph.add_node("extract_requirements", extract_requirements_node)
    graph.add_node("generate_cad", generate_cad_node)
    graph.add_node("run_geometry_checks", run_geometry_checks_node)
    graph.add_node("revise_specification", revise_specification_node)
    graph.add_node("evaluate_materials", evaluate_materials_node)
    graph.add_node("generate_report", generate_report_node)

    graph.set_entry_point("extract_requirements")
    graph.add_edge("extract_requirements", "generate_cad")
    graph.add_edge("generate_cad", "run_geometry_checks")

    graph.add_conditional_edges(
        "run_geometry_checks",
        should_revise,
        {
            "revise": "revise_specification",
            "proceed": "evaluate_materials"
        }
    )
    graph.add_edge("revise_specification", "generate_cad")
    graph.add_edge("evaluate_materials", "generate_report")
    graph.add_edge("generate_report", END)

    return graph.compile()


def run_design_pipeline(user_prompt: str) -> DesignState:
    """Execute end-to-end design pipeline."""
    app = build_medcad_graph()
    initial_state: DesignState = {
        "user_request": user_prompt,
        "revision_count": 0,
        "errors": []
    }
    return app.invoke(initial_state)
