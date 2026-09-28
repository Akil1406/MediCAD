"""Backend CAD Engine Package."""

from .base import SolidMesh, CADResult, create_hollow_cylinder_mesh
from .tube import build_tube
from .catheter import build_catheter
from .tapered_tube import build_tapered_tube
from .connector import build_connector
from .injector import build_injector
from .plunger import build_plunger
from .assembly import build_syringe_assembly
from .exporters import export_step, export_stl, export_obj, export_design_package

CAD_BUILDERS = {
    "tube": build_tube,
    "catheter": build_catheter,
    "tapered_tube": build_tapered_tube,
    "connector": build_connector,
    "injector": build_injector,
    "plunger": build_plunger,
}

__all__ = [
    "SolidMesh",
    "CADResult",
    "create_hollow_cylinder_mesh",
    "build_tube",
    "build_catheter",
    "build_tapered_tube",
    "build_connector",
    "build_injector",
    "build_plunger",
    "build_syringe_assembly",
    "export_step",
    "export_stl",
    "export_obj",
    "export_design_package",
    "CAD_BUILDERS",
]
