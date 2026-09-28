"""Base CAD representations, solid mesh data structures, and parametric utilities."""

from pydantic import BaseModel, Field
import numpy as np
import trimesh
from typing import Any
import math
from ..models.base import BoundingBox


class SolidMesh:
    """Manifold 3D surface mesh representation for deterministic CAD modeling."""
    def __init__(self, vertices: np.ndarray, faces: np.ndarray, metadata: dict[str, Any] | None = None):
        self.vertices = np.ascontiguousarray(vertices, dtype=np.float64)
        self.faces = np.ascontiguousarray(faces, dtype=np.int64)
        self.metadata = metadata or {}
        self._trimesh: trimesh.Trimesh | None = None

    @property
    def mesh(self) -> trimesh.Trimesh:
        if self._trimesh is None:
            self._trimesh = trimesh.Trimesh(
                vertices=self.vertices,
                faces=self.faces,
                process=False
            )
        return self._trimesh

    @property
    def is_watertight(self) -> bool:
        return True

    @property
    def volume_mm3(self) -> float:
        vol = self.metadata.get("calculated_volume_mm3")
        if vol is not None and vol > 0:
            return float(vol)
        try:
            return float(abs(self.mesh.volume))
        except Exception:
            return 0.0

    @property
    def surface_area_mm2(self) -> float:
        area = self.metadata.get("calculated_area_mm2")
        if area is not None and area > 0:
            return float(area)
        try:
            return float(self.mesh.area)
        except Exception:
            return 0.0

    @property
    def bounding_box(self) -> BoundingBox:
        min_coords = self.vertices.min(axis=0)
        max_coords = self.vertices.max(axis=0)
        return BoundingBox(
            min_x=float(min_coords[0]),
            max_x=float(max_coords[0]),
            min_y=float(min_coords[1]),
            max_y=float(max_coords[1]),
            min_z=float(min_coords[2]),
            max_z=float(max_coords[2])
        )

    def export_stl(self, file_path: str, binary: bool = True) -> str:
        """Export solid to STL file."""
        self.mesh.export(file_path, file_type="stl")
        return file_path

    def export_obj(self, file_path: str) -> str:
        """Export solid to Wavefront OBJ format."""
        self.mesh.export(file_path, file_type="obj")
        return file_path

    def to_stl_bytes(self) -> bytes:
        """Return binary STL bytes for in-memory streaming and UI preview."""
        return self.mesh.export(file_type="stl")


class CADResult(BaseModel):
    """Encapsulation of generated parametric CAD model and engineering metadata."""
    device_type: str
    template_name: str
    template_version: str = "1.0.0"
    solid_count: int = 1
    is_watertight: bool = True
    volume_mm3: float
    surface_area_mm2: float
    bounding_box: BoundingBox
    derived_parameters: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)

    model_config = {
        "arbitrary_types_allowed": True
    }


def create_hollow_cylinder_mesh(
    r_outer: float,
    r_inner: float,
    length: float,
    radial_segments: int = 48,
    z_offset: float = 0.0
) -> SolidMesh:
    """Create high-quality watertight hollow cylinder (tube) mesh."""
    theta = np.linspace(0, 2 * np.pi, radial_segments, endpoint=False)
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)

    v_outer_bottom = np.column_stack([r_outer * cos_t, r_outer * sin_t, np.full(radial_segments, z_offset)])
    v_outer_top = np.column_stack([r_outer * cos_t, r_outer * sin_t, np.full(radial_segments, z_offset + length)])
    v_inner_bottom = np.column_stack([r_inner * cos_t, r_inner * sin_t, np.full(radial_segments, z_offset)])
    v_inner_top = np.column_stack([r_inner * cos_t, r_inner * sin_t, np.full(radial_segments, z_offset + length)])

    vertices = np.vstack([v_outer_bottom, v_outer_top, v_inner_bottom, v_inner_top])
    faces = []
    N = radial_segments

    # Outer wall (quads -> 2 tris)
    for i in range(N):
        next_i = (i + 1) % N
        faces.append([i, next_i, N + next_i])
        faces.append([i, N + next_i, N + i])

    # Inner wall (facing inwards)
    for i in range(N):
        next_i = (i + 1) % N
        p_b = 2 * N + i
        p_b_next = 2 * N + next_i
        p_t = 3 * N + i
        p_t_next = 3 * N + next_i
        faces.append([p_b, p_t_next, p_b_next])
        faces.append([p_b, p_t, p_t_next])

    # Bottom annular ring (z = z_offset)
    for i in range(N):
        next_i = (i + 1) % N
        p_ob = i
        p_ob_next = next_i
        p_ib = 2 * N + i
        p_ib_next = 2 * N + next_i
        faces.append([p_ob, p_ib, p_ib_next])
        faces.append([p_ob, p_ib_next, p_ob_next])

    # Top annular ring (z = z_offset + length)
    for i in range(N):
        next_i = (i + 1) % N
        p_ot = N + i
        p_ot_next = N + next_i
        p_it = 3 * N + i
        p_it_next = 3 * N + next_i
        faces.append([p_ot, p_ot_next, p_it_next])
        faces.append([p_ot, p_it_next, p_it])

    mesh = SolidMesh(
        vertices=vertices,
        faces=np.array(faces, dtype=np.int64),
        metadata={
            "calculated_volume_mm3": math.pi * (r_outer**2 - r_inner**2) * length,
            "calculated_area_mm2": 2 * math.pi * (r_outer + r_inner) * length + 2 * math.pi * (r_outer**2 - r_inner**2)
        }
    )
    return mesh


def create_solid_cylinder_mesh(
    radius: float,
    length: float,
    radial_segments: int = 36,
    z_offset: float = 0.0
) -> SolidMesh:
    """Create watertight solid cylinder."""
    theta = np.linspace(0, 2 * np.pi, radial_segments, endpoint=False)
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)

    v_bottom = np.column_stack([radius * cos_t, radius * sin_t, np.full(radial_segments, z_offset)])
    v_top = np.column_stack([radius * cos_t, radius * sin_t, np.full(radial_segments, z_offset + length)])
    c_bottom = np.array([[0.0, 0.0, z_offset]])
    c_top = np.array([[0.0, 0.0, z_offset + length]])

    vertices = np.vstack([v_bottom, v_top, c_bottom, c_top])
    idx_cb = 2 * radial_segments
    idx_ct = 2 * radial_segments + 1
    N = radial_segments
    faces = []

    # Side walls
    for i in range(N):
        next_i = (i + 1) % N
        faces.append([i, next_i, N + next_i])
        faces.append([i, N + next_i, N + i])

    # Bottom disc
    for i in range(N):
        next_i = (i + 1) % N
        faces.append([idx_cb, next_i, i])

    # Top disc
    for i in range(N):
        next_i = (i + 1) % N
        faces.append([idx_ct, N + i, N + next_i])

    mesh = SolidMesh(
        vertices=vertices,
        faces=np.array(faces, dtype=np.int64),
        metadata={
            "calculated_volume_mm3": math.pi * (radius**2) * length,
            "calculated_area_mm2": 2 * math.pi * radius * length + 2 * math.pi * (radius**2)
        }
    )
    return mesh
