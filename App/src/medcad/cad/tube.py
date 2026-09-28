"""Parametric CAD generator for straight hollow tubes."""

from ..models.specs import TubeSpec
from .base import SolidMesh, CADResult, create_hollow_cylinder_mesh


def build_tube(spec: TubeSpec) -> tuple[SolidMesh, CADResult]:
    """Generate deterministic 3D solid geometry for a hollow tube."""
    r_outer = spec.outer_diameter_mm / 2.0
    r_inner = spec.inner_diameter_mm / 2.0
    length = spec.length_mm

    mesh = create_hollow_cylinder_mesh(
        r_outer=r_outer,
        r_inner=r_inner,
        length=length,
        radial_segments=64
    )

    cad_result = CADResult(
        device_type="tube",
        template_name="deterministic_tube_v1",
        template_version="1.0.0",
        solid_count=1,
        is_watertight=mesh.is_watertight,
        volume_mm3=mesh.volume_mm3,
        surface_area_mm2=mesh.surface_area_mm2,
        bounding_box=mesh.bounding_box,
        derived_parameters={
            "wall_thickness_mm": spec.wall_thickness_mm,
            "outer_radius_mm": spec.outer_radius_mm,
            "inner_radius_mm": spec.inner_radius_mm,
            "cross_sectional_area_mm2": spec.cross_sectional_area_mm2,
            "lumen_volume_mm3": spec.lumen_volume_mm3,
            "material_volume_mm3": spec.material_volume_mm3,
            "aspect_ratio": length / spec.outer_diameter_mm
        }
    )

    return mesh, cad_result
