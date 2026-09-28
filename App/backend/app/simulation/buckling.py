"""Euler column buckling simulation for catheter and tube pushability."""

import math
from ..models.specs import TubeSpec, CatheterSpec
from ..models.materials import Material
from ..models.simulation import BucklingSimulationResult


class ColumnBucklingSimulator:
    def run(
        self,
        spec: TubeSpec | CatheterSpec,
        material: Material,
        applied_push_force_n: float = 2.0,
        end_condition: str = "pinned_pinned"
    ) -> BucklingSimulationResult:
        r_o = spec.outer_diameter_mm / 2.0
        r_i = spec.inner_diameter_mm / 2.0
        length_mm = spec.length_mm

        inertia_mm4 = (math.pi / 4.0) * (r_o**4 - r_i**4)
        elastic_modulus_mpa = material.elastic_modulus_mpa

        unsupported_length_mm = min(length_mm, 50.0)
        k_factor = 1.0 if end_condition == "pinned_pinned" else 2.0
        effective_length_mm = k_factor * unsupported_length_mm

        critical_load_n = (math.pi**2 * elastic_modulus_mpa * inertia_mm4) / (effective_length_mm**2)
        critical_load_gf = critical_load_n * 101.97162

        safety_factor = critical_load_n / max(applied_push_force_n, 1e-4)

        if safety_factor >= 2.0:
            status = "PASS"
            notes = f"Adequate axial pushability (P_crit = {critical_load_n:.2f} N, SF = {safety_factor:.2f})."
        elif safety_factor >= 1.0:
            status = "WARNING"
            notes = f"Risk of shaft buckling under tortuous insertion (SF = {safety_factor:.2f})."
        else:
            status = "FAIL"
            notes = f"Shaft will buckle under standard {applied_push_force_n:.1f} N push force! (P_crit = {critical_load_n:.2f} N)."

        return BucklingSimulationResult(
            material_name=material.name,
            elastic_modulus_mpa=elastic_modulus_mpa,
            moment_of_inertia_mm4=inertia_mm4,
            effective_length_mm=effective_length_mm,
            critical_buckling_load_n=critical_load_n,
            critical_buckling_load_gf=critical_load_gf,
            applied_force_n=applied_push_force_n,
            buckling_safety_factor=safety_factor,
            status=status,
            solver_notes=notes
        )
