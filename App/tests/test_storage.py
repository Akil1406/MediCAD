"""Unit tests for design versioning and database storage."""

from medcad.storage import DesignStorage, VersionComparator


def test_design_version_creation_and_diff(tmp_path):
    db_path = tmp_path / "test_design_storage.db"
    storage = DesignStorage(db_path=db_path)

    spec_v1 = {
        "device_type": "tube",
        "length_mm": 100.0,
        "outer_diameter_mm": 3.0,
        "inner_diameter_mm": 2.0
    }
    cad_prop_v1 = {"volume_mm3": 392.7, "is_watertight": True}
    val_v1 = {"passed": True, "issues": []}

    # Save V1
    v1_num = storage.save_design_version(
        design_id="DES_TEST_TUBE",
        title="Cardiovascular Catheter Shaft",
        device_type="tube",
        specification=spec_v1,
        cad_properties=cad_prop_v1,
        validation_report=val_v1,
        user_prompt="Initial catheter shaft"
    )
    assert v1_num == 1

    # Save V2 (modified length)
    spec_v2 = dict(spec_v1)
    spec_v2["length_mm"] = 150.0

    v2_num = storage.save_design_version(
        design_id="DES_TEST_TUBE",
        title="Cardiovascular Catheter Shaft",
        device_type="tube",
        specification=spec_v2,
        cad_properties={"volume_mm3": 589.0, "is_watertight": True},
        validation_report=val_v1,
        user_prompt="Make it 150 mm long"
    )
    assert v2_num == 2

    history = storage.get_design_history("DES_TEST_TUBE")
    assert len(history) == 2

    # Check diff
    diff = VersionComparator.compute_diff(history[0], history[1])
    assert diff["changed_parameters_count"] == 1
    assert "length_mm" in diff["differences"]
    assert diff["differences"]["length_mm"]["from_value"] == 100.0
    assert diff["differences"]["length_mm"]["to_value"] == 150.0
    assert diff["differences"]["length_mm"]["delta"] == 50.0
