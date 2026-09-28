"""Hagen-Poiseuille syringe fluid flow and plunger actuation force solver."""

import math
from .base import BaseSimulator
from ..models.specs import InjectorSpec
from ..models.simulation import DispenseSimulationResult


class SyringeFlowSimulator(BaseSimulator):
    """Calculates flow pressure drop through nozzle/needle and manual plunger depression force."""

    def run(
        self,
        spec: InjectorSpec,
        flow_rate_ml_s: float = 0.5,
        fluid_viscosity_cp: float = 1.0,
        needle_gauge: int | None = 23,
        needle_length_mm: float = 25.0
    ) -> DispenseSimulationResult:
        # Standard hypodermic needle inner diameters (ISO 9626)
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

        # Determine effective orifice diameter and length
        if needle_gauge and needle_gauge in needle_id_map:
            d_orifice_mm = needle_id_map[needle_gauge]
            l_orifice_mm = needle_length_mm
        else:
            d_orifice_mm = spec.nozzle_inner_diameter_mm
            l_orifice_mm = spec.nozzle_length_mm

        r_orifice_m = (d_orifice_mm / 2.0) / 1000.0
        l_orifice_m = l_orifice_mm / 1000.0

        # Viscosity: 1 cP = 0.001 Pa*s
        mu_pa_s = fluid_viscosity_cp * 0.001

        # Volumetric flow rate: 1 mL/s = 1e-6 m3/s
        q_m3_s = flow_rate_ml_s * 1e-6

        # Hagen-Poiseuille law: Delta P = (8 * mu * L * Q) / (pi * r^4) [in Pascals]
        delta_p_pa = (8.0 * mu_pa_s * l_orifice_m * q_m3_s) / (math.pi * (r_orifice_m**4))
        delta_p_bar = delta_p_pa / 100000.0

        # Plunger hydraulic force: F_hyd = Delta P * A_barrel
        # Barrel radius in meters
        r_barrel_m = (spec.body_inner_diameter_mm / 2.0) / 1000.0
        a_barrel_m2 = math.pi * (r_barrel_m**2)

        plunger_hyd_force_n = delta_p_pa * a_barrel_m2
        seal_friction_n = 2.5  # Typical medical silicone/rubber stopper friction
        total_thumb_force_n = plunger_hyd_force_n + seal_friction_n
        total_thumb_force_kgf = total_thumb_force_n / 9.80665

        # Ergonomic assessment (ISO 11608 standard thumb force < 15-20 N for manual syringe)
        if total_thumb_force_n <= 15.0:
            status = "PASS"
            ergo = f"Comfortable manual actuation force ({total_thumb_force_n:.1f} N <= 15 N ISO threshold)."
        elif total_thumb_force_n <= 30.0:
            status = "WARNING"
            ergo = f"Elevated thumb force ({total_thumb_force_n:.1f} N). May cause operator fatigue during repetitive dispensing."
        else:
            status = "FAIL"
            ergo = f"Excessive thumb force ({total_thumb_force_n:.1f} N > 30 N limit)! High risk of syringe stalling or needle blow-off."

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
