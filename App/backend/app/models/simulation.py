"""Simulation input configs and result models."""

from pydantic import BaseModel, Field
from typing import Literal


class SimulationConfigRequest(BaseModel):
    simulation_type: Literal["burst_pressure", "column_buckling", "syringe_dispense_force"]
    design_id: str | None = None
    material_id: str = "MAT_PEBAX_7233"
    operating_pressure_bar: float = 10.0
    axial_push_force_n: float = 1.5
    dispense_flow_rate_ml_s: float = 0.5
    fluid_viscosity_cp: float = 1.0
    needle_gauge_g: int = 23
    needle_length_mm: float = 25.0
    custom_dimensions: dict = Field(default_factory=dict)


class BurstSimulationResult(BaseModel):
    simulation_type: Literal["burst_pressure"] = "burst_pressure"
    material_name: str
    yield_strength_mpa: float
    operating_pressure_bar: float
    operating_pressure_mpa: float
    hoop_stress_mpa: float
    radial_stress_mpa: float
    von_mises_stress_mpa: float
    yield_safety_factor: float
    theoretical_burst_pressure_bar: float
    status: Literal["PASS", "WARNING", "FAIL"]
    solver_notes: str
    assumptions: list[str] = Field(
        default_factory=lambda: [
            "Uniform axisymmetric internal pressure",
            "Lamé thick/thin wall elastic cylinder formulation",
            "Isotropic, homogeneous material behavior at room temperature"
        ]
    )


class BucklingSimulationResult(BaseModel):
    simulation_type: Literal["column_buckling"] = "column_buckling"
    material_name: str
    elastic_modulus_mpa: float
    moment_of_inertia_mm4: float
    effective_length_mm: float
    critical_buckling_load_n: float
    critical_buckling_load_gf: float
    applied_force_n: float
    buckling_safety_factor: float
    status: Literal["PASS", "WARNING", "FAIL"]
    solver_notes: str
    assumptions: list[str] = Field(
        default_factory=lambda: [
            "Euler column formula with pinned-guided end conditions",
            "Linear elastic deformation regime without initial curvature",
            "Pure axial compressive loading"
        ]
    )


class DispenseSimulationResult(BaseModel):
    simulation_type: Literal["syringe_dispense_force"] = "syringe_dispense_force"
    barrel_inner_diameter_mm: float
    nozzle_inner_diameter_mm: float
    flow_rate_ml_s: float
    fluid_viscosity_cp: float
    needle_gauge: int | None = None
    pressure_drop_nozzle_bar: float
    plunger_hydraulic_force_n: float
    estimated_seal_friction_n: float
    total_thumb_force_n: float
    total_thumb_force_kgf: float
    status: Literal["PASS", "WARNING", "FAIL"]
    ergonomic_assessment: str
    assumptions: list[str] = Field(
        default_factory=lambda: [
            "Hagen-Poiseuille laminar viscous flow in cylindrical conduits",
            "Incompressible Newtonian fluid",
            "Elastomeric plunger stopper friction estimated at 2.5 N"
        ]
    )
