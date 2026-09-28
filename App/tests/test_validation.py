"""Unit tests for geometric validation and manufacturing design rules."""

from medcad.models.specs import TubeSpec, CatheterSpec
from medcad.cad import build_tube
from medcad.validation import run_full_validation, validate_geometric_spec


def test_validation_pass():
    spec = TubeSpec(length_mm=100.0, outer_diameter_mm=3.0, inner_diameter_mm=2.0)
    mesh, cad_res = build_tube(spec)
    report = run_full_validation(spec, cad_res)

    assert report.passed is True
    assert report.solid_valid is True
    assert report.has_errors is False
    assert report.wall_thickness_mm == 0.5


def test_validation_thin_wall_error():
    # Wall thickness = (1.05 - 1.0)/2 = 0.025 mm < 0.10 mm threshold
    spec = TubeSpec(length_mm=100.0, outer_diameter_mm=1.05, inner_diameter_mm=1.0)
    mesh, cad_res = build_tube(spec)
    report = run_full_validation(spec, cad_res)

    assert report.passed is False
    assert report.has_errors is True
    assert any(i.code == "GEO_WALL_TOO_THIN" for i in report.issues)


def test_validation_high_aspect_ratio_warning():
    # Length = 500 mm, OD = 2.0 mm -> Aspect ratio = 250 > 50
    spec = TubeSpec(length_mm=500.0, outer_diameter_mm=2.0, inner_diameter_mm=1.0)
    mesh, cad_res = build_tube(spec)
    report = run_full_validation(spec, cad_res)

    assert report.has_warnings is True
    assert any(i.code == "GEO_HIGH_ASPECT_RATIO" for i in report.issues)
