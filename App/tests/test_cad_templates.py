"""Unit tests for deterministic CAD templates."""

import math
from medcad.models.specs import (
    TubeSpec, CatheterSpec, TaperedTubeSpec,
    ConnectorSpec, InjectorSpec, PlungerSpec, AssemblySpec
)
from medcad.cad import (
    build_tube, build_catheter, build_tapered_tube,
    build_connector, build_injector, build_plunger,
    build_syringe_assembly
)


def test_build_tube():
    spec = TubeSpec(length_mm=100.0, outer_diameter_mm=3.0, inner_diameter_mm=2.0)
    mesh, cad_res = build_tube(spec)

    assert cad_res.device_type == "tube"
    assert cad_res.is_watertight is True
    assert cad_res.volume_mm3 > 0
    assert cad_res.surface_area_mm2 > 0

    # Theoretical volume = pi * (1.5^2 - 1.0^2) * 100 = 125 * pi ~ 392.7 mm3
    expected_vol = math.pi * (1.5**2 - 1.0**2) * 100.0
    assert math.isclose(cad_res.volume_mm3, expected_vol, rel_tol=0.05)


def test_build_catheter():
    spec = CatheterSpec(
        length_mm=150.0,
        outer_diameter_mm=2.0,
        inner_diameter_mm=1.2,
        tip_length_mm=5.0,
        has_luer_hub=True
    )
    mesh, cad_res = build_catheter(spec)

    assert cad_res.device_type == "catheter"
    assert cad_res.is_watertight is True
    assert cad_res.volume_mm3 > 0
    assert cad_res.derived_parameters["french_size_fr"] == 6.0


def test_build_tapered_tube():
    spec = TaperedTubeSpec(
        length_mm=80.0,
        proximal_outer_diameter_mm=4.0,
        distal_outer_diameter_mm=2.0,
        inner_diameter_mm=1.2
    )
    mesh, cad_res = build_tapered_tube(spec)

    assert cad_res.device_type == "tapered_tube"
    assert cad_res.is_watertight is True
    assert cad_res.volume_mm3 > 0


def test_build_connector():
    spec = ConnectorSpec(length_mm=20.0, outer_diameter_mm=6.5, inner_diameter_mm=2.5)
    mesh, cad_res = build_connector(spec)

    assert cad_res.device_type == "connector"
    assert cad_res.is_watertight is True
    assert cad_res.volume_mm3 > 0


def test_build_injector():
    spec = InjectorSpec(
        body_length_mm=80.0,
        body_outer_diameter_mm=16.0,
        body_inner_diameter_mm=14.0,
        nozzle_length_mm=10.0,
        nozzle_outer_diameter_mm=4.0,
        nozzle_inner_diameter_mm=1.8,
        flange_width_mm=24.0,
        flange_thickness_mm=2.5
    )
    mesh, cad_res = build_injector(spec)

    assert cad_res.device_type == "injector"
    assert cad_res.is_watertight is True
    assert cad_res.volume_mm3 > 0
    assert cad_res.derived_parameters["usable_volume_ml"] > 10.0


def test_build_plunger():
    spec = PlungerSpec(
        plunger_length_mm=90.0,
        rod_diameter_mm=6.0,
        head_outer_diameter_mm=13.9,
        head_length_mm=8.0
    )
    mesh, cad_res = build_plunger(spec)

    assert cad_res.device_type == "plunger"
    assert cad_res.is_watertight is True
    assert cad_res.volume_mm3 > 0


def test_build_assembly():
    inj_spec = InjectorSpec(
        body_length_mm=80.0,
        body_outer_diameter_mm=16.0,
        body_inner_diameter_mm=14.0,
        flange_width_mm=24.0
    )
    plu_spec = PlungerSpec(
        plunger_length_mm=90.0,
        rod_diameter_mm=6.0,
        head_outer_diameter_mm=13.9
    )
    assy_spec = AssemblySpec(injector_spec=inj_spec, plunger_spec=plu_spec)

    mesh, cad_res, analysis = build_syringe_assembly(assy_spec)
    assert cad_res.solid_count == 2
    assert analysis["interference_detected"] is False
    assert analysis["fit_status"] == "OPTIMAL"
