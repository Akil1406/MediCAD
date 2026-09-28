"""Parametric CAD generator for catheter shafts with atraumatic tips and proximal luer hubs."""

import numpy as np
import math
from ..models.specs import CatheterSpec
from .base import SolidMesh, CADResult


def build_catheter(spec: CatheterSpec) -> tuple[SolidMesh, CADResult]:
    """Generate deterministic 3D solid geometry for catheter with tip and hub."""
    r_shaft_od = spec.outer_diameter_mm / 2.0
    r_shaft_id = spec.inner_diameter_mm / 2.0
    r_tip_od = spec.effective_tip_od_mm / 2.0
    r_tip_id = r_shaft_id

    total_len = spec.length_mm
    tip_len = spec.tip_length_mm
    shaft_len = total_len - tip_len
    hub_len = spec.hub_length_mm if spec.has_luer_hub else 0.0

    radial_segments = 64
    theta = np.linspace(0, 2 * np.pi, radial_segments, endpoint=False)
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)
    N = radial_segments

    # Construct continuous profile rings along Z:
    # 1. Distal tip end (Z = 0)
    # 2. Tip-to-shaft transition (Z = tip_len)
    # 3. Shaft proximal end (Z = tip_len + shaft_len = total_len)
    # 4. Optional Hub flare (Z = total_len + hub_len * 0.4)
    # 5. Optional Hub outer socket (Z = total_len + hub_len)

    z_levels = [0.0, tip_len, total_len]
    r_od_levels = [r_tip_od, r_shaft_od, r_shaft_od]
    r_id_levels = [r_tip_id, r_shaft_id, r_shaft_id]

    if spec.has_luer_hub:
        r_hub_outer_mid = r_shaft_od * 2.2
        r_hub_outer_end = r_shaft_od * 2.8
        r_hub_inner_end = r_shaft_id * 1.8

        z_levels.extend([total_len + hub_len * 0.4, total_len + hub_len])
        r_od_levels.extend([r_hub_outer_mid, r_hub_outer_end])
        r_id_levels.extend([r_shaft_id * 1.3, r_hub_inner_end])

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
    # Outer lofted quads
    for ring_idx in range(num_levels - 1):
        base_cur = ring_idx * N
        base_next = (ring_idx + 1) * N
        for i in range(N):
            next_i = (i + 1) % N
            faces.append([base_cur + i, base_cur + next_i, base_next + next_i])
            faces.append([base_cur + i, base_next + next_i, base_next + i])

    # Inner lofted quads (reverse winding for inward normal)
    inner_offset = num_levels * N
    for ring_idx in range(num_levels - 1):
        base_cur = inner_offset + ring_idx * N
        base_next = inner_offset + (ring_idx + 1) * N
        for i in range(N):
            next_i = (i + 1) % N
            faces.append([base_cur + i, base_next + next_i, base_cur + next_i])
            faces.append([base_cur + i, base_next + i, base_next + next_i])

    # Distal end annular cap (Z = 0)
    for i in range(N):
        next_i = (i + 1) % N
        p_o = i
        p_o_next = next_i
        p_i = inner_offset + i
        p_i_next = inner_offset + next_i
        faces.append([p_o, p_i, p_i_next])
        faces.append([p_o, p_i_next, p_o_next])

    # Proximal end annular cap (Z = top)
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
        metadata={
            "calculated_volume_mm3": math.pi * (r_shaft_od**2 - r_shaft_id**2) * shaft_len +
                                     math.pi * ((r_tip_od + r_shaft_od)/2)**2 * tip_len,
            "french_size": spec.french_size
        }
    )

    cad_result = CADResult(
        device_type="catheter",
        template_name="deterministic_catheter_v1",
        template_version="1.0.0",
        solid_count=1,
        is_watertight=mesh.is_watertight,
        volume_mm3=mesh.volume_mm3,
        surface_area_mm2=mesh.surface_area_mm2,
        bounding_box=mesh.bounding_box,
        derived_parameters={
            "french_size_fr": spec.french_size,
            "shaft_wall_thickness_mm": spec.shaft_wall_thickness_mm,
            "tip_outer_diameter_mm": spec.effective_tip_od_mm,
            "tip_length_mm": spec.tip_length_mm,
            "has_luer_hub": spec.has_luer_hub,
            "total_effective_length_mm": total_len + hub_len,
            "aspect_ratio": spec.length_mm / spec.outer_diameter_mm
        }
    )

    return mesh, cad_result
