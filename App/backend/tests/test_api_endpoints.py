"""Integration tests for FastAPI REST API endpoints."""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "SAFETY & REGULATORY" in data["disclaimer"] or "NOTICE" in data["disclaimer"]


def test_create_design_endpoint():
    payload = {
        "title": "Coronary Catheter Shaft",
        "device_type": "catheter",
        "prompt": "Vascular catheter 150 mm long, 2.0 mm OD, 1.2 mm ID, 5 mm tip.",
        "units": "mm"
    }
    response = client.post("/api/v1/designs", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "design_id" in data
    assert data["device_type"] == "catheter"
    assert data["version"] == 1
    assert data["specification"]["outer_diameter_mm"] == 2.0
    assert "mesh_stl_bytes" in data


def test_update_design_parameters():
    # First create
    init_payload = {
        "title": "Extrusion Tube",
        "device_type": "tube",
        "dimensions": {"length_mm": 100.0, "outer_diameter_mm": 3.0, "inner_diameter_mm": 2.0}
    }
    res_create = client.post("/api/v1/designs", json=init_payload)
    assert res_create.status_code == 201
    design_id = res_create.json()["design_id"]

    # Patch parameters
    patch_payload = {
        "parameters": {"length_mm": 160.0, "outer_diameter_mm": 3.2},
        "prompt": "Lengthen to 160 mm and increase OD"
    }
    res_patch = client.patch(f"/api/v1/designs/{design_id}/parameters", json=patch_payload)
    assert res_patch.status_code == 200
    data = res_patch.json()
    assert data["version"] == 2
    assert data["specification"]["length_mm"] == 160.0
    assert data["specification"]["outer_diameter_mm"] == 3.2


def test_cad_build_endpoint():
    payload = {
        "device_type": "connector",
        "length_mm": 25.0,
        "outer_diameter_mm": 6.5,
        "inner_diameter_mm": 2.5,
        "barb_count": 3
    }
    response = client.post("/api/v1/cad/build", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "stl_base64" in data
    assert data["cad_properties"]["volume_mm3"] > 0


def test_materials_ranking_endpoint():
    payload = {
        "flexibility_preference": "flexible",
        "required_sterilization_method": "EtO"
    }
    response = client.post("/api/v1/materials/rank", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["candidates"]) > 0
    top = data["candidates"][0]
    assert top["engineering_fit"] == "Excellent"


def test_simulation_endpoint():
    payload = {
        "simulation_type": "burst_pressure",
        "material_id": "MAT_PEBAX_7233",
        "operating_pressure_bar": 12.0,
        "custom_dimensions": {"length_mm": 100.0, "outer_diameter_mm": 3.0, "inner_diameter_mm": 2.0}
    }
    response = client.post("/api/v1/simulations", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["simulation"]["simulation_type"] == "burst_pressure"
    assert data["simulation"]["yield_safety_factor"] > 0


def test_ai_agent_endpoint():
    payload = {"prompt": "Create an injector syringe barrel with 80 mm body and 14 mm bore."}
    response = client.post("/api/v1/ai/agent", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert data["target_device_type"] == "injector"
    assert data["specification"]["body_inner_diameter_mm"] == 14.0
