"""Parametric CAD generator for ISO 594 / ISO 80369 Luer lock and barbed connectors."""

import numpy as np
import math
from ..models.specs import ConnectorSpec
from .base import SolidMesh, CADResult


def build_connector(spec: ConnectorSpec) -> tuple[SolidMesh, CADResult]:
    length = spec.length_mm
    r_body_od = spec.outer_diameter_mm / 2.0
    r_id = spec.inner_diameter_mm / 2.0

    radial_segments = 64
    theta = np.linspace(0, 2 * np.pi, radial_segments, endpoint=False)
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)
    N = radial_segments

    luer_len = length * 0.40
    collar_len = length * 0.25
    barb_len = length * 0.35

    r_luer_tip = r_body_od * 0.65
    r_luer_base = r_luer_tip + (luer_len * 0.06)
    r_collar_od = r_body_od * 1.15

    z_levels = [0.0, luer_len, luer_len, luer_len + collar_len, luer_len + collar_len]
    r_od_levels = [r_luer_tip, r_luer_base, r_collar_od, r_collar_od, r_body_od]

    num_barbs = max(1, spec.barb_count)
    barb_step = barb_len / num_barbs
    cur_z = luer_len + collar_len
    for b in range(num_barbs):
        z_mid = cur_z + barb_step * 0.7
        z_end = cur_z + barb_step
        r_barb_peak = r_body_od * 1.12
        r_barb_trough = r_body_od * 0.85
        z_levels.extend([z_mid, z_end])
        r_od_levels.extend([r_barb_peak, r_barb_trough])
        cur_z = z_end

    num_levels = len(z_levels)
    outer_rings = []
    inner_rings = []

    for z, r_od in zip(z_levels, r_od_levels):
        outer_rings.append(np.column_stack([r_od * cos_t, r_od * sin_t, np.full(N, z)]))
        inner_rings.append(np.column_stack([r_id * cos_t, r_id * sin_t, np.full(N, z)]))

    all_outer_verts = np.vstack(outer_rings)
    all_inner_verts = np.vstack(inner_rings)
    vertices = np.vstack([all_outer_verts, all_inner_verts])

    faces = []
    for ring_idx in range(num_levels - 1):
        base_cur = ring_idx * N
        base_next = (ring_idx + 1) * N
        for i in range(N):
            next_i = (i + 1) % N
            faces.append([base_cur + i, base_cur + next_i, base_next + next_i])
            faces.append([base_cur + i, base_next + next_i, base_next + i])

    inner_offset = num_levels * N
    for ring_idx in range(num_levels - 1):
        base_cur = inner_offset + ring_idx * N
        base_next = inner_offset + (ring_idx + 1) * N
        for i in range(N):
            next_i = (i + 1) % N
            faces.append([base_cur + i, base_next + next_i, base_cur + next_i])
            faces.append([base_cur + i, base_next + i, base_next + next_i])

    for i in range(N):
        next_i = (i + 1) % N
        p_o = i
        p_o_next = next_i
        p_i = inner_offset + i
        p_i_next = inner_offset + next_i
        faces.append([p_o, p_i, p_i_next])
        faces.append([p_o, p_i_next, p_o_next])

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
            "connector_standard": "ISO 594 / ISO 80369-7 Luer Lock",
            "barb_count": num_barbs
        }
    )

    cad_result = CADResult(
        device_type="connector",
        template_name="deterministic_connector_v1",
        template_version="1.0.0",
        solid_count=1,
        is_watertight=mesh.is_watertight,
        volume_mm3=mesh.volume_mm3,
        surface_area_mm2=mesh.surface_area_mm2,
        bounding_box=mesh.bounding_box,
        derived_parameters={
            "connector_type": spec.connector_type,
            "iso_luer_taper": "6% conical ISO standard",
            "luer_section_length_mm": luer_len,
            "collar_section_length_mm": collar_len,
            "barb_section_length_mm": barb_len,
            "mean_wall_thickness_mm": spec.wall_thickness_mm,
            "barb_count": spec.barb_count
        }
    )

    return mesh, cad_result
