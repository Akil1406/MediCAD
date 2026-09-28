"""Parametric CAD generator for syringe plungers and pistons."""

import numpy as np
import math
from ..models.specs import PlungerSpec
from .base import SolidMesh, CADResult


def build_plunger(spec: PlungerSpec) -> tuple[SolidMesh, CADResult]:
    """Generate deterministic 3D solid geometry for syringe plunger."""
    r_thumb = spec.thumb_rest_diameter_mm / 2.0
    r_rod = spec.rod_diameter_mm / 2.0
    r_head = spec.head_outer_diameter_mm / 2.0

    p_len = spec.plunger_length_mm
    h_len = spec.head_length_mm
    t_th = spec.thumb_rest_thickness_mm
    rod_len = p_len - h_len - t_th

    radial_segments = 48
    theta = np.linspace(0, 2 * np.pi, radial_segments, endpoint=False)
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)
    N = radial_segments

    # Construct along Z from distal piston face (Z=0) to proximal thumb press top:
    # 0. Distal piston face (Z=0)
    # 1. Distal piston head body (Z=h_len)
    # 2. Transition step to rod (Z=h_len)
    # 3. Rod end before thumb disc (Z=h_len + rod_len)
    # 4. Thumb disc step out (Z=h_len + rod_len)
    # 5. Thumb disc top face (Z=p_len)

    z_levels = [
        0.0,
        h_len,
        h_len,
        h_len + rod_len,
        h_len + rod_len,
        p_len
    ]
    r_levels = [
        r_head,
        r_head,
        r_rod,
        r_rod,
        r_thumb,
        r_thumb
    ]

    num_levels = len(z_levels)
    rings = []
    for z, r in zip(z_levels, r_levels):
        rings.append(np.column_stack([r * cos_t, r * sin_t, np.full(N, z)]))

    # Center points for bottom and top caps
    c_bottom = np.array([[0.0, 0.0, 0.0]])
    c_top = np.array([[0.0, 0.0, p_len]])

    all_ring_verts = np.vstack(rings)
    idx_cb = len(all_ring_verts)
    idx_ct = len(all_ring_verts) + 1
    vertices = np.vstack([all_ring_verts, c_bottom, c_top])

    faces = []
    # Side walls and steps
    for ring_idx in range(num_levels - 1):
        base_cur = ring_idx * N
        base_next = (ring_idx + 1) * N
        for i in range(N):
            next_i = (i + 1) % N
            faces.append([base_cur + i, base_cur + next_i, base_next + next_i])
            faces.append([base_cur + i, base_next + next_i, base_next + i])

    # Bottom cap (piston face, facing -Z)
    for i in range(N):
        next_i = (i + 1) % N
        faces.append([idx_cb, next_i, i])

    # Top cap (thumb press face, facing +Z)
    top_base = (num_levels - 1) * N
    for i in range(N):
        next_i = (i + 1) % N
        faces.append([idx_ct, top_base + i, top_base + next_i])

    mesh = SolidMesh(
        vertices=vertices,
        faces=np.array(faces, dtype=np.int64),
        metadata={
            "calculated_volume_mm3": math.pi * (r_head**2) * h_len +
                                     math.pi * (r_rod**2) * rod_len +
                                     math.pi * (r_thumb**2) * t_th
        }
    )

    cad_result = CADResult(
        device_type="plunger",
        template_name="deterministic_plunger_v1",
        template_version="1.0.0",
        solid_count=1,
        is_watertight=mesh.is_watertight,
        volume_mm3=mesh.volume_mm3,
        surface_area_mm2=mesh.surface_area_mm2,
        bounding_box=mesh.bounding_box,
        derived_parameters={
            "total_length_mm": spec.plunger_length_mm,
            "head_diameter_mm": spec.head_outer_diameter_mm,
            "rod_diameter_mm": spec.rod_diameter_mm,
            "thumb_rest_diameter_mm": spec.thumb_rest_diameter_mm,
            "head_cross_section_area_mm2": math.pi * (r_head**2),
            "rod_aspect_ratio": rod_len / spec.rod_diameter_mm
        }
    )

    return mesh, cad_result
