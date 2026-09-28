"""Data models for engineering simulations (burst pressure, buckling, flow rate)."""

from pydantic import BaseModel, Field
from typing import Literal


class SimulationConfig(BaseModel):
    """Configuration input for engineering simulations."""
    simulation_type: Literal["burst_pressure", "column_buckling", "syringe_dispense_force"]
    material_id: str
    operating_pressure_bar: float | None = Field(default=None, gt=0)
    axial_push_force_n: float | None = Field(default=None, gt=0)
    dispense_flow_rate_ml_s: float | None = Field(default=None, gt=0)
    fluid_viscosity_cp: float = Field(default=1.0, gt=0, description="Fluid dynamic viscosity in centipoise (water=1.0)")
    needle_gauge_g: int | None = Field(default=None, ge=14, le=34)
    needle_length_mm: float = Field(default=25.0, gt=0)
    safety_factor_target: float = Field(default=2.0, gt=1.0)


class BurstSimulationResult(BaseModel):
    """Lamé equation hoop & radial stress output."""
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
    """Euler column buckling load output for pushability."""
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
            "Euler column formula with pinned-guided or fixed-free end conditions",
            "Linear elastic deformation regime without initial curvature",
            "Pure axial compressive loading"
        ]
    )


class DispenseSimulationResult(BaseModel):
    """Syringe flow pressure drop and plunger actuation force output."""
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
