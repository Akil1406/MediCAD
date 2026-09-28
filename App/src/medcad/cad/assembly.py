"""Multi-component assembly generator and interference analysis."""

import numpy as np
import trimesh
from ..models.specs import AssemblySpec, InjectorSpec, PlungerSpec
from .base import SolidMesh, CADResult
from .injector import build_injector
from .plunger import build_plunger


def build_syringe_assembly(spec: AssemblySpec) -> tuple[SolidMesh, CADResult, dict]:
    """Generate mated assembly of Syringe Barrel + Plunger with clearance analysis."""
    injector_mesh, injector_cad = build_injector(spec.injector_spec)
    plunger_mesh, plunger_cad = build_plunger(spec.plunger_spec)

    # Position plunger inserted into barrel (e.g. 50% stroke insertion)
    insertion_depth_z = spec.injector_spec.nozzle_length_mm + spec.injector_spec.body_length_mm * 0.4
    plunger_verts = plunger_mesh.vertices.copy()
    plunger_verts[:, 2] += insertion_depth_z

    # Combined mesh
    n_inj_v = len(injector_mesh.vertices)
    combined_verts = np.vstack([injector_mesh.vertices, plunger_verts])
    combined_faces = np.vstack([injector_mesh.faces, plunger_mesh.faces + n_inj_v])

    assembly_solid = SolidMesh(
        vertices=combined_verts,
        faces=combined_faces,
        metadata={"assembly_name": spec.assembly_name}
    )

    # Clearance & Interference analysis
    barrel_bore = spec.injector_spec.body_inner_diameter_mm
    plunger_head = spec.plunger_spec.head_outer_diameter_mm
    diametral_clearance = barrel_bore - plunger_head
    radial_clearance = diametral_clearance / 2.0

    interference_detected = plunger_head > barrel_bore
    clearance_status = "INTERFERENCE" if interference_detected else ("OPTIMAL" if 0.02 <= radial_clearance <= 0.10 else "LOOSE")

    analysis = {
        "barrel_bore_diameter_mm": barrel_bore,
        "plunger_head_diameter_mm": plunger_head,
        "diametral_clearance_mm": diametral_clearance,
        "radial_clearance_mm": radial_clearance,
        "interference_detected": interference_detected,
        "fit_status": clearance_status,
        "stroke_length_mm": spec.injector_spec.body_length_mm - spec.plunger_spec.head_length_mm
    }

    cad_result = CADResult(
        device_type="assembly",
        template_name="deterministic_assembly_v1",
        template_version="1.0.0",
        solid_count=2,
        is_watertight=assembly_solid.is_watertight,
        volume_mm3=injector_cad.volume_mm3 + plunger_cad.volume_mm3,
        surface_area_mm2=injector_cad.surface_area_mm2 + plunger_cad.surface_area_mm2,
        bounding_box=assembly_solid.bounding_box,
        derived_parameters=analysis
    )

    return assembly_solid, cad_result, analysis
