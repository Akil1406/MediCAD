"""Unit tests for LangChain tools and LangGraph orchestrator."""

import json
from medcad.tools import (
    validate_device_spec,
    generate_device_cad,
    search_materials,
    run_geometry_checks
)
from medcad.agents import run_design_pipeline


def test_tool_validate_device_spec():
    valid_payload = json.dumps({
        "device_type": "tube",
        "length_mm": 120.0,
        "outer_diameter_mm": 3.0,
        "inner_diameter_mm": 2.0
    })
    res_str = validate_device_spec.invoke({"spec_json": valid_payload})
    res = json.loads(res_str)
    assert res["valid"] is True

    invalid_payload = json.dumps({
        "device_type": "tube",
        "length_mm": 120.0,
        "outer_diameter_mm": 2.0,
        "inner_diameter_mm": 2.5
    })
    res_str = validate_device_spec.invoke({"spec_json": invalid_payload})
    res = json.loads(res_str)
    assert res["valid"] is False


def test_tool_generate_device_cad():
    payload = json.dumps({
        "device_type": "tube",
        "length_mm": 80.0,
        "outer_diameter_mm": 2.5,
        "inner_diameter_mm": 1.5
    })
    res_str = generate_device_cad.invoke({"device_type": "tube", "spec_json": payload})
    res = json.loads(res_str)
    assert res["success"] is True
    assert res["volume_mm3"] > 0


def test_tool_search_materials():
    payload = json.dumps({
        "flexibility_preference": "flexible",
        "required_sterilization_method": "EtO"
    })
    res_str = search_materials.invoke({"requirements_json": payload})
    res = json.loads(res_str)
    assert res["success"] is True
    assert len(res["candidates"]) > 0


def test_orchestrator_pipeline_execution():
    prompt = "Create a catheter with length 150 mm, outer diameter 2.2 mm, inner diameter 1.4 mm, and tip 5 mm."
    final_state = run_design_pipeline(prompt)

    assert final_state["status"] == "COMPLETED"
    assert final_state["target_device_type"] == "catheter"
    assert final_state["cad_result"]["is_watertight"] is True
    assert len(final_state["material_candidates"]) > 0
    assert len(final_state["engineering_report"]) > 100
