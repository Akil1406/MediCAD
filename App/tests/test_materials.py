"""Unit tests for medical material database and deterministic ranking."""

from medcad.materials import MaterialDatabase, evaluate_and_rank_materials
from medcad.models.materials import MaterialRequirements


def test_materials_database_seeding(tmp_path):
    db_path = tmp_path / "test_materials.db"
    db = MaterialDatabase(db_path=db_path)
    materials = db.get_all_materials()

    assert len(materials) >= 8
    mat_ids = [m.material_id for m in materials]
    assert "MAT_PEBAX_7233" in mat_ids
    assert "MAT_PTFE_EXTRUDED" in mat_ids
    assert "MAT_SS_316L" in mat_ids


def test_material_ranking_high_strength(tmp_path):
    db_path = tmp_path / "test_materials.db"
    db = MaterialDatabase(db_path=db_path)

    reqs = MaterialRequirements(
        minimum_tensile_strength_mpa=500.0,
        flexibility_preference="rigid"
    )
    ranked = evaluate_and_rank_materials(reqs, db=db)

    assert len(ranked) > 0
    top_mat = ranked[0].material
    assert top_mat.tensile_strength_mpa >= 500.0
    assert top_mat.family == "metal"


def test_material_ranking_flexible_catheter(tmp_path):
    db_path = tmp_path / "test_materials.db"
    db = MaterialDatabase(db_path=db_path)

    reqs = MaterialRequirements(
        flexibility_preference="flexible",
        preferred_manufacturing_method="Extrusion",
        required_sterilization_method="EtO"
    )
    ranked = evaluate_and_rank_materials(reqs, db=db)

    assert len(ranked) > 0
    top_match = ranked[0]
    assert top_match.score >= 0.85
    assert top_match.engineering_fit == "Excellent"
