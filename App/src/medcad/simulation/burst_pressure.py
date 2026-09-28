"""Lamé equation burst pressure and hoop stress simulation solver."""

import math
from .base import BaseSimulator
from ..models.specs import TubeSpec, CatheterSpec
from ..models.materials import Material
from ..models.simulation import SimulationConfig, BurstSimulationResult


class BurstPressureSimulator(BaseSimulator):
    """Calculates internal pressure containment, hoop stress, and burst safety factors."""

    def run(
        self,
        spec: TubeSpec | CatheterSpec,
        material: Material,
        operating_pressure_bar: float = 6.0
    ) -> BurstSimulationResult:
        # Convert bar to MPa (1 bar = 0.1 MPa)
        p_mpa = operating_pressure_bar * 0.10

        r_o = spec.outer_diameter_mm / 2.0
        r_i = spec.inner_diameter_mm / 2.0
        sigma_yield = material.yield_strength_mpa or (material.tensile_strength_mpa * 0.75)

        # Lamé equations for internal pressure in thick-walled cylinder
        # Max hoop stress occurs at internal surface (r = r_i)
        hoop_stress_mpa = p_mpa * ((r_o**2 + r_i**2) / (r_o**2 - r_i**2))
        radial_stress_mpa = -p_mpa

        # Von Mises equivalent stress at inner surface
        von_mises_mpa = math.sqrt(
            hoop_stress_mpa**2 - hoop_stress_mpa * radial_stress_mpa + radial_stress_mpa**2
        )

        safety_factor = sigma_yield / max(von_mises_mpa, 1e-6)

        # Theoretical burst pressure (elastic limit yield)
        burst_pressure_mpa = sigma_yield * ((r_o**2 - r_i**2) / (r_o**2 + r_i**2))
        burst_pressure_bar = burst_pressure_mpa * 10.0

        if safety_factor >= 2.0:
            status = "PASS"
            notes = f"Design satisfies safety target (SF = {safety_factor:.2f} >= 2.0)."
        elif safety_factor >= 1.0:
            status = "WARNING"
            notes = f"Marginal safety factor (SF = {safety_factor:.2f}). Consider increasing wall thickness."
        else:
            status = "FAIL"
            notes = f"Operating pressure exceeds material yield limit! (SF = {safety_factor:.2f} < 1.0)."

        return BurstSimulationResult(
            material_name=material.name,
            yield_strength_mpa=sigma_yield,
            operating_pressure_bar=operating_pressure_bar,
            operating_pressure_mpa=p_mpa,
            hoop_stress_mpa=hoop_stress_mpa,
            radial_stress_mpa=radial_stress_mpa,
            von_mises_stress_mpa=von_mises_mpa,
            yield_safety_factor=safety_factor,
            theoretical_burst_pressure_bar=burst_pressure_bar,
            status=status,
            solver_notes=notes
        )
