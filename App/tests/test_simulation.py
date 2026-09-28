"""Unit tests for engineering simulation solvers."""

from medcad.models.specs import TubeSpec, InjectorSpec
from medcad.materials.catalog import MEDICAL_MATERIALS_CATALOG
from medcad.simulation import (
    BurstPressureSimulator,
    ColumnBucklingSimulator,
    SyringeFlowSimulator
)


def test_burst_pressure_simulation():
    tube_spec = TubeSpec(length_mm=100.0, outer_diameter_mm=3.0, inner_diameter_mm=2.0)
    # Pebax 7233
    mat = next(m for m in MEDICAL_MATERIALS_CATALOG if m.material_id == "MAT_PEBAX_7233")

    sim = BurstPressureSimulator()
    result = sim.run(spec=tube_spec, material=mat, operating_pressure_bar=10.0)

    assert result.simulation_type == "burst_pressure"
    assert result.hoop_stress_mpa > 0
    assert result.yield_safety_factor > 0
    assert result.status in ("PASS", "WARNING", "FAIL")


def test_column_buckling_simulation():
    tube_spec = TubeSpec(length_mm=150.0, outer_diameter_mm=2.0, inner_diameter_mm=1.2)
    mat = next(m for m in MEDICAL_MATERIALS_CATALOG if m.material_id == "MAT_PEBAX_7233")

    sim = ColumnBucklingSimulator()
    result = sim.run(spec=tube_spec, material=mat, applied_push_force_n=1.5)

    assert result.simulation_type == "column_buckling"
    assert result.critical_buckling_load_n > 0
    assert result.critical_buckling_load_gf > 0


def test_syringe_flow_simulation():
    inj_spec = InjectorSpec(
        body_length_mm=80.0,
        body_outer_diameter_mm=16.0,
        body_inner_diameter_mm=14.0,
        nozzle_length_mm=10.0,
        nozzle_outer_diameter_mm=4.0,
        nozzle_inner_diameter_mm=1.8,
        flange_width_mm=24.0
    )

    sim = SyringeFlowSimulator()
    result = sim.run(spec=inj_spec, flow_rate_ml_s=0.5, fluid_viscosity_cp=1.0, needle_gauge=23)

    assert result.simulation_type == "syringe_dispense_force"
    assert result.total_thumb_force_n > 0
    assert result.status in ("PASS", "WARNING", "FAIL")
