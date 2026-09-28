"""STEP, STL, OBJ, and design package bundle exporters."""

from pathlib import Path
import json
import datetime
from .base import SolidMesh, CADResult
from ..config import EXPORTS_DIR, APP_NAME, APP_VERSION


def generate_step_file_content(mesh: SolidMesh, part_name: str = "MEDCAD_PART") -> str:
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    vertices = mesh.vertices
    faces = mesh.faces

    lines = [
        "ISO-10303-21;",
        "HEADER;",
        f"FILE_DESCRIPTION(('MediCAD Parametric Prototyping STEP Model'), '2;1');",
        f"FILE_NAME('{part_name}.step', '{timestamp}', ('MediCAD Engine'), ('Medical CAD Builder'), 'MediCAD CAD Core {APP_VERSION}', 'Python / MediCAD', '');",
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));",
        "ENDSEC;",
        "DATA;",
        "#1=APPLICATION_CONTEXT('core data for automotive and medical design');",
        "#2=APPLICATION_PROTOCOL_DEFINITION('international standard', 'automotive_design', 2000, #1);",
        "#3=PRODUCT_CONTEXT('part definition', #1, 'mechanical');",
        f"#4=PRODUCT('{part_name}', '{part_name}', 'Parametric Medical CAD Model', (#3));",
        f"#5=PRODUCT_DEFINITION_FORMATION_WITH_SPECIFIED_SOURCE('1.0', '', #4, .NOT_KNOWN.);",
        "#6=PRODUCT_DEFINITION('design', '', #5, #3);",
        "#7=PRODUCT_DEFINITION_SHAPE('', '', #6);",
        "#8=SHAPE_REPRESENTATION('', (#9), #10);",
        "#9=AXIS2_PLACEMENT_3D('', #11, #12, #13);",
        "#10=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#14)) GLOBAL_UNIT_ASSIGNED_CONTEXT((#15,#16,#17)) REPRESENTATION_CONTEXT('Context3D', '3D Context'));",
        "#11=CARTESIAN_POINT('', (0., 0., 0.));",
        "#12=DIRECTION('', (0., 0., 1.));",
        "#13=DIRECTION('', (1., 0., 0.));",
        "#14=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-05), #15, 'distance_accuracy_value', 'confusion accuracy');",
        "#15=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI., .METRE.));",
        "#16=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($, .RADIAN.));",
        "#17=(NAMED_UNIT(*) SI_UNIT($, .STERADIAN.) SOLID_ANGLE_UNIT());",
        "#18=SHAPE_DEFINITION_REPRESENTATION(#7, #8);"
    ]

    entity_id = 19
    vert_map = {}
    for i, v in enumerate(vertices):
        lines.append(f"#{entity_id}=CARTESIAN_POINT('', ({v[0]:.6f}, {v[1]:.6f}, {v[2]:.6f}));")
        vert_map[i] = entity_id
        entity_id += 1

    face_entities = []
    for f in faces[:1200]:
        p1, p2, p3 = vert_map[f[0]], vert_map[f[1]], vert_map[f[2]]
        poly_id = entity_id
        lines.append(f"#{poly_id}=POLY_LOOP('', (#{p1}, #{p2}, #{p3}));")
        entity_id += 1
        bound_id = entity_id
        lines.append(f"#{bound_id}=FACE_OUTER_BOUND('', #{poly_id}, .T.);")
        entity_id += 1
        face_id = entity_id
        lines.append(f"#{face_id}=FACE_SURFACE('', (#{bound_id}), #{face_id+1}, .T.);")
        entity_id += 1
        lines.append(f"#{face_id+1}=PLANE('', #9);")
        entity_id += 2
        face_entities.append(face_id)

    faces_list_str = ",".join(f"#{fid}" for fid in face_entities)
    brep_shell_id = entity_id
    lines.append(f"#{brep_shell_id}=CLOSED_SHELL('', ({faces_list_str}));")
    entity_id += 1
    brep_solid_id = entity_id
    lines.append(f"#{brep_solid_id}=FACETTED_BREP('{part_name}_SOLID', #{brep_shell_id});")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")

    return "\n".join(lines)


def export_step(mesh: SolidMesh, file_path: str | Path, part_name: str = "MEDCAD_PART") -> Path:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = generate_step_file_content(mesh, part_name)
    path.write_text(content, encoding="utf-8")
    return path


def export_stl(mesh: SolidMesh, file_path: str | Path) -> Path:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    mesh.export_stl(str(path))
    return path


def export_obj(mesh: SolidMesh, file_path: str | Path) -> Path:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    mesh.export_obj(str(path))
    return path


def export_design_package(
    mesh: SolidMesh,
    cad_result: CADResult,
    spec_dict: dict,
    validation_dict: dict,
    design_id: str,
    version: int = 1,
    base_dir: Path | None = None
) -> dict[str, str]:
    target_dir = (base_dir or EXPORTS_DIR) / f"{design_id}_v{version}"
    target_dir.mkdir(parents=True, exist_ok=True)

    prefix = f"{cad_result.device_type}_v{version}"
    step_path = target_dir / f"{prefix}.step"
    stl_path = target_dir / f"{prefix}.stl"
    obj_path = target_dir / f"{prefix}.obj"
    json_path = target_dir / f"{prefix}_spec.json"
    manifest_path = target_dir / "manifest.json"

    export_step(mesh, step_path, part_name=f"{cad_result.device_type.upper()}_V{version}")
    export_stl(mesh, stl_path)
    export_obj(mesh, obj_path)

    bundle_metadata = {
        "app_name": APP_NAME,
        "app_version": APP_VERSION,
        "design_id": design_id,
        "version": version,
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "device_type": cad_result.device_type,
        "template_name": cad_result.template_name,
        "template_version": cad_result.template_version,
        "authoritative_cad_file": step_path.name,
        "preview_mesh_file": stl_path.name,
        "specification": spec_dict,
        "cad_derived_properties": cad_result.derived_parameters,
        "validation_summary": validation_dict,
        "regulatory_disclaimer": "Engineering prototyping artifact. Not approved for clinical or in-vivo medical use."
    }

    json_path.write_text(json.dumps(spec_dict, indent=2), encoding="utf-8")
    manifest_path.write_text(json.dumps(bundle_metadata, indent=2), encoding="utf-8")

    return {
        "package_directory": str(target_dir),
        "step_file": str(step_path),
        "stl_file": str(stl_path),
        "obj_file": str(obj_path),
        "spec_json": str(json_path),
        "manifest_json": str(manifest_path)
    }
