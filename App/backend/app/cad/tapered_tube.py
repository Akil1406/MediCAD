"""Parametric CAD generator for tapered hollow shafts."""

import numpy as np
import math
from ..models.specs import TaperedTubeSpec
from .base import SolidMesh, CADResult


def build_tapered_tube(spec: TaperedTubeSpec) -> tuple[SolidMesh, CADResult]:
    r_prox_od = spec.proximal_outer_diameter_mm / 2.0
    r_dist_od = spec.distal_outer_diameter_mm / 2.0
    r_id = spec.inner_diameter_mm / 2.0
    length = spec.length_mm

    radial_segments = 64
    theta = np.linspace(0, 2 * np.pi, radial_segments, endpoint=False)
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)
    N = radial_segments

    v_od_distal = np.column_stack([r_dist_od * cos_t, r_dist_od * sin_t, np.zeros(N)])
    v_od_proximal = np.column_stack([r_prox_od * cos_t, r_prox_od * sin_t, np.full(N, length)])
    v_id_distal = np.column_stack([r_id * cos_t, r_id * sin_t, np.zeros(N)])
    v_id_proximal = np.column_stack([r_id * cos_t, r_id * sin_t, np.full(N, length)])

    vertices = np.vstack([v_od_distal, v_od_proximal, v_id_distal, v_id_proximal])
    faces = []

    for i in range(N):
        next_i = (i + 1) % N
        faces.append([i, next_i, N + next_i])
        faces.append([i, N + next_i, N + i])

    for i in range(N):
        next_i = (i + 1) % N
        p_b = 2 * N + i
        p_b_next = 2 * N + next_i
        p_t = 3 * N + i
        p_t_next = 3 * N + next_i
        faces.append([p_b, p_t_next, p_b_next])
        faces.append([p_b, p_t, p_t_next])

    for i in range(N):
        next_i = (i + 1) % N
        p_o = i
        p_o_next = next_i
        p_i = 2 * N + i
        p_i_next = 2 * N + next_i
        faces.append([p_o, p_i, p_i_next])
        faces.append([p_o, p_i_next, p_o_next])

    for i in range(N):
        next_i = (i + 1) % N
        p_o = N + i
        p_o_next = N + next_i
        p_i = 3 * N + i
        p_i_next = 3 * N + next_i
        faces.append([p_o, p_o_next, p_i_next])
        faces.append([p_o, p_i_next, p_i])

    vol = (math.pi * length / 3.0) * (r_prox_od**2 + r_dist_od**2 + r_prox_od * r_dist_od) - math.pi * (r_id**2) * length

    mesh = SolidMesh(
        vertices=vertices,
        faces=np.array(faces, dtype=np.int64),
        metadata={"calculated_volume_mm3": vol}
    )

    taper_angle_deg = math.degrees(math.atan(abs(r_prox_od - r_dist_od) / length))

    cad_result = CADResult(
        device_type="tapered_tube",
        template_name="deterministic_tapered_tube_v1",
        template_version="1.0.0",
        solid_count=1,
        is_watertight=mesh.is_watertight,
        volume_mm3=mesh.volume_mm3,
        surface_area_mm2=mesh.surface_area_mm2,
        bounding_box=mesh.bounding_box,
        derived_parameters={
            "taper_angle_deg": taper_angle_deg,
            "min_wall_thickness_mm": spec.min_wall_thickness_mm,
            "max_wall_thickness_mm": spec.max_wall_thickness_mm,
            "proximal_od_mm": spec.proximal_outer_diameter_mm,
            "distal_od_mm": spec.distal_outer_diameter_mm,
            "taper_ratio": abs(spec.proximal_outer_diameter_mm - spec.distal_outer_diameter_mm) / length
        }
    )

    return mesh, cad_result
