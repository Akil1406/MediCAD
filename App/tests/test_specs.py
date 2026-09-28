"""Unit tests for Pydantic device specifications."""

import pytest
from pydantic import ValidationError
from medcad.models.specs import (
    TubeSpec, CatheterSpec, TaperedTubeSpec,
    ConnectorSpec, InjectorSpec, PlungerSpec, AssemblySpec
)


def test_valid_tube_spec():
    spec = TubeSpec(length_mm=100.0, outer_diameter_mm=3.0, inner_diameter_mm=2.0)
    assert spec.wall_thickness_mm == 0.5
    assert spec.outer_radius_mm == 1.5
    assert spec.inner_radius_mm == 1.0
    assert spec.lumen_volume_mm3 > 0
    assert spec.material_volume_mm3 > 0


def test_invalid_tube_spec_id_ge_od():
    with pytest.raises(ValidationError) as exc:
        TubeSpec(length_mm=100.0, outer_diameter_mm=2.0, inner_diameter_mm=2.0)
    assert "must be strictly less than" in str(exc.value)

    with pytest.raises(ValidationError):
        TubeSpec(length_mm=100.0, outer_diameter_mm=2.0, inner_diameter_mm=2.5)


def test_invalid_tube_spec_negative_dims():
    with pytest.raises(ValidationError):
        TubeSpec(length_mm=-50.0, outer_diameter_mm=3.0, inner_diameter_mm=2.0)

    with pytest.raises(ValidationError):
        TubeSpec(length_mm=100.0, outer_diameter_mm=0.0, inner_diameter_mm=0.0)


def test_valid_catheter_spec():
    spec = CatheterSpec(
        length_mm=150.0,
        outer_diameter_mm=2.0,
        inner_diameter_mm=1.2,
        tip_length_mm=5.0,
        tip_angle_deg=15.0
    )
    assert spec.shaft_wall_thickness_mm == 0.4
    assert spec.french_size == 6.0  # 2.0 mm * 3 = 6 Fr
    assert spec.effective_tip_od_mm > spec.inner_diameter_mm


def test_invalid_catheter_tip_length():
    with pytest.raises(ValidationError) as exc:
        CatheterSpec(
            length_mm=10.0,
            outer_diameter_mm=2.0,
            inner_diameter_mm=1.2,
            tip_length_mm=15.0
        )
    assert "cannot be greater than or equal to total catheter length" in str(exc.value)


def test_valid_injector_spec():
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
    assert spec.barrel_wall_thickness_mm == 1.0
    assert spec.nozzle_wall_thickness_mm == 1.1
    assert spec.usable_volume_ml > 0  # ~12.3 mL


def test_valid_plunger_spec():
    spec = PlungerSpec(
        plunger_length_mm=90.0,
        rod_diameter_mm=6.0,
        head_outer_diameter_mm=13.9,
        head_length_mm=8.0
    )
    assert spec.rod_diameter_mm < spec.head_outer_diameter_mm
