"""Parametric CAD generator for injector / syringe barrel bodies."""

import numpy as np
import math
from ..models.specs import InjectorSpec
from .base import SolidMesh, CADResult


def build_injector(spec: InjectorSpec) -> tuple[SolidMesh, CADResult]:
    """Generate deterministic 3D solid geometry for syringe barrel body."""
    r_barrel_od = spec.body_outer_diameter_mm / 2.0
    r_barrel_id = spec.body_inner_diameter_mm / 2.0
    r_nozzle_od = spec.nozzle_outer_diameter_mm / 2.0
    r_nozzle_id = spec.nozzle_inner_diameter_mm / 2.0
    r_flange_rad = spec.flange_width_mm / 2.0

    b_len = spec.body_length_mm
    n_len = spec.nozzle_length_mm
    flange_th = spec.flange_thickness_mm

    radial_segments = 64
    theta = np.linspace(0, 2 * np.pi, radial_segments, endpoint=False)
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)
    N = radial_segments

    # Construct along Z axis from nozzle tip (Z=0) to proximal flange top:
    # 0. Nozzle tip (Z = 0)
    # 1. Nozzle base / transition start (Z = n_len)
    # 2. Barrel base / transition end (Z = n_len + 2.0)
    # 3. Barrel body before flange (Z = n_len + b_len - flange_th)
    # 4. Flange bottom (Z = n_len + b_len - flange_th)
    # 5. Flange top (Z = n_len + b_len)

    z_levels = [
        0.0,
        n_len,
        n_len + 2.0,
        n_len + b_len - flange_th,
        n_len + b_len - flange_th,
        n_len + b_len
    ]
    r_od_levels = [
        r_nozzle_od,
        r_nozzle_od * 1.05,
        r_barrel_od,
        r_barrel_od,
        r_flange_rad,
        r_flange_rad
    ]
    r_id_levels = [
        r_nozzle_id,
        r_nozzle_id,
        r_barrel_id,
        r_barrel_id,
        r_barrel_id,
        r_barrel_id
    ]

    num_levels = len(z_levels)
    outer_rings = []
    inner_rings = []

    for z, r_od, r_id in zip(z_levels, r_od_levels, r_id_levels):
        outer_rings.append(np.column_stack([r_od * cos_t, r_od * sin_t, np.full(N, z)]))
        inner_rings.append(np.column_stack([r_id * cos_t, r_id * sin_t, np.full(N, z)]))

    all_outer_verts = np.vstack(outer_rings)
    all_inner_verts = np.vstack(inner_rings)
    vertices = np.vstack([all_outer_verts, all_inner_verts])

    faces = []
    # Outer walls
    for ring_idx in range(num_levels - 1):
        base_cur = ring_idx * N
        base_next = (ring_idx + 1) * N
        for i in range(N):
            next_i = (i + 1) % N
            faces.append([base_cur + i, base_cur + next_i, base_next + next_i])
            faces.append([base_cur + i, base_next + next_i, base_next + i])

    # Inner walls
    inner_offset = num_levels * N
    for ring_idx in range(num_levels - 1):
        base_cur = inner_offset + ring_idx * N
        base_next = inner_offset + (ring_idx + 1) * N
        for i in range(N):
            next_i = (i + 1) % N
            faces.append([base_cur + i, base_next + next_i, base_cur + next_i])
            faces.append([base_cur + i, base_next + i, base_next + next_i])

    # Distal nozzle tip cap (Z = 0)
    for i in range(N):
        next_i = (i + 1) % N
        p_o = i
        p_o_next = next_i
        p_i = inner_offset + i
        p_i_next = inner_offset + next_i
        faces.append([p_o, p_i, p_i_next])
        faces.append([p_o, p_i_next, p_o_next])

    # Proximal flange opening cap (Z = top)
    top_outer_base = (num_levels - 1) * N
    top_inner_base = inner_offset + (num_levels - 1) * N
    for i in range(N):
        next_i = (i + 1) % N
        p_o = top_outer_base + i
        p_o_next = top_outer_base + next_i
        p_i = top_inner_base + i
        p_i_next = top_inner_base + next_i
        faces.append([p_o, p_o_next, p_i_next])
        faces.append([p_o, p_i_next, p_i])

    mesh = SolidMesh(
        vertices=vertices,
        faces=np.array(faces, dtype=np.int64),
        metadata={"usable_volume_ml": spec.usable_volume_ml}
    )

    cad_result = CADResult(
        device_type="injector",
        template_name="deterministic_injector_v1",
        template_version="1.0.0",
        solid_count=1,
        is_watertight=mesh.is_watertight,
        volume_mm3=mesh.volume_mm3,
        surface_area_mm2=mesh.surface_area_mm2,
        bounding_box=mesh.bounding_box,
        derived_parameters={
            "usable_volume_ml": spec.usable_volume_ml,
            "barrel_wall_thickness_mm": spec.barrel_wall_thickness_mm,
            "nozzle_wall_thickness_mm": spec.nozzle_wall_thickness_mm,
            "total_overall_length_mm": spec.body_length_mm + spec.nozzle_length_mm,
            "flange_outer_diameter_mm": spec.flange_width_mm,
            "barrel_cross_section_area_mm2": math.pi * (r_barrel_id**2)
        }
    )

    return mesh, cad_result
