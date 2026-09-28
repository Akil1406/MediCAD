"""Hagen-Poiseuille syringe fluid flow and plunger actuation force solver."""

import math
from ..models.specs import InjectorSpec
from ..models.simulation import DispenseSimulationResult


class SyringeFlowSimulator:
    def run(
        self,
        spec: InjectorSpec,
        flow_rate_ml_s: float = 0.5,
        fluid_viscosity_cp: float = 1.0,
        needle_gauge: int | None = 23,
        needle_length_mm: float = 25.0
    ) -> DispenseSimulationResult:
        needle_id_map = {
            18: 0.838,
            20: 0.603,
            21: 0.514,
            22: 0.413,
            23: 0.337,
            25: 0.260,
            27: 0.210,
            30: 0.159,
        }

        if needle_gauge and needle_gauge in needle_id_map:
            d_orifice_mm = needle_id_map[needle_gauge]
            l_orifice_mm = needle_length_mm
        else:
            d_orifice_mm = spec.nozzle_inner_diameter_mm
            l_orifice_mm = spec.nozzle_length_mm

        r_orifice_m = (d_orifice_mm / 2.0) / 1000.0
        l_orifice_m = l_orifice_mm / 1000.0

        mu_pa_s = fluid_viscosity_cp * 0.001
        q_m3_s = flow_rate_ml_s * 1e-6

        delta_p_pa = (8.0 * mu_pa_s * l_orifice_m * q_m3_s) / (math.pi * (r_orifice_m**4))
        delta_p_bar = delta_p_pa / 100000.0

        r_barrel_m = (spec.body_inner_diameter_mm / 2.0) / 1000.0
        a_barrel_m2 = math.pi * (r_barrel_m**2)

        plunger_hyd_force_n = delta_p_pa * a_barrel_m2
        seal_friction_n = 2.5
        total_thumb_force_n = plunger_hyd_force_n + seal_friction_n
        total_thumb_force_kgf = total_thumb_force_n / 9.80665

        if total_thumb_force_n <= 15.0:
            status = "PASS"
            ergo = f"Comfortable manual actuation force ({total_thumb_force_n:.1f} N <= 15 N ISO threshold)."
        elif total_thumb_force_n <= 30.0:
            status = "WARNING"
            ergo = f"Elevated thumb force ({total_thumb_force_n:.1f} N). May cause operator fatigue during repetitive dispensing."
        else:
            status = "FAIL"
            ergo = f"Excessive thumb force ({total_thumb_force_n:.1f} N > 30 N limit)! High risk of syringe stalling."

        return DispenseSimulationResult(
            barrel_inner_diameter_mm=spec.body_inner_diameter_mm,
            nozzle_inner_diameter_mm=spec.nozzle_inner_diameter_mm,
            flow_rate_ml_s=flow_rate_ml_s,
            fluid_viscosity_cp=fluid_viscosity_cp,
            needle_gauge=needle_gauge,
            pressure_drop_nozzle_bar=delta_p_bar,
            plunger_hydraulic_force_n=plunger_hyd_force_n,
            estimated_seal_friction_n=seal_friction_n,
            total_thumb_force_n=total_thumb_force_n,
            total_thumb_force_kgf=total_thumb_force_kgf,
            status=status,
            ergonomic_assessment=ergo
        )
