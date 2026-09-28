"""FastAPI routes for physics-based engineering simulations."""

from fastapi import APIRouter, HTTPException
from ...models.simulation import SimulationConfigRequest
from ...models.specs import TubeSpec, CatheterSpec, InjectorSpec
from ...materials import MaterialDatabase
from ...simulation import BurstPressureSimulator, ColumnBucklingSimulator, SyringeFlowSimulator


router = APIRouter(prefix="/simulations", tags=["Simulations"])
db = MaterialDatabase()
burst_sim = BurstPressureSimulator()
buckling_sim = ColumnBucklingSimulator()
syringe_sim = SyringeFlowSimulator()


@router.post("")
def run_simulation(payload: SimulationConfigRequest):
    """Run physics-based deterministic engineering simulation."""
    mat = db.get_material_by_id(payload.material_id)
    if not mat:
        # Default fallback to first material in DB
        all_m = db.get_all_materials()
        mat = all_m[0] if all_m else None

    if not mat:
        raise HTTPException(status_code=400, detail="No material found in database.")

    dims = payload.custom_dimensions

    if payload.simulation_type == "burst_pressure":
        length = float(dims.get("length_mm", 100.0))
        od = float(dims.get("outer_diameter_mm", 3.0))
        id_val = float(dims.get("inner_diameter_mm", 2.0))
        tube_spec = TubeSpec(length_mm=length, outer_diameter_mm=od, inner_diameter_mm=id_val)
        result = burst_sim.run(tube_spec, mat, operating_pressure_bar=payload.operating_pressure_bar)
        return {"simulation": result.model_dump()}

    elif payload.simulation_type == "column_buckling":
        length = float(dims.get("length_mm", 150.0))
        od = float(dims.get("outer_diameter_mm", 2.0))
        id_val = float(dims.get("inner_diameter_mm", 1.2))
        cath_spec = TubeSpec(length_mm=length, outer_diameter_mm=od, inner_diameter_mm=id_val)
        result = buckling_sim.run(cath_spec, mat, applied_push_force_n=payload.axial_push_force_n)
        return {"simulation": result.model_dump()}

    elif payload.simulation_type == "syringe_dispense_force":
        b_len = float(dims.get("body_length_mm", 80.0))
        b_od = float(dims.get("body_outer_diameter_mm", 16.0))
        b_id = float(dims.get("body_inner_diameter_mm", 14.0))
        flange = float(dims.get("flange_width_mm", 24.0))
        inj_spec = InjectorSpec(body_length_mm=b_len, body_outer_diameter_mm=b_od, body_inner_diameter_mm=b_id, flange_width_mm=flange)
        result = syringe_sim.run(
            spec=inj_spec,
            flow_rate_ml_s=payload.dispense_flow_rate_ml_s,
            fluid_viscosity_cp=payload.fluid_viscosity_cp,
            needle_gauge=payload.needle_gauge_g,
            needle_length_mm=payload.needle_length_mm
        )
        return {"simulation": result.model_dump()}

    raise HTTPException(status_code=400, detail=f"Unsupported simulation type: '{payload.simulation_type}'")
