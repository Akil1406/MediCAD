"""Medical materials data models and candidate rankings."""

from pydantic import BaseModel, Field
from typing import Literal


class MaterialRequirements(BaseModel):
    minimum_tensile_strength_mpa: float | None = None
    minimum_elastic_modulus_mpa: float | None = None
    maximum_elastic_modulus_mpa: float | None = None
    max_operating_temp_c: float | None = None
    preferred_manufacturing_method: str | None = None
    required_sterilization_method: str | None = None
    flexibility_preference: Literal["rigid", "semi_rigid", "flexible", "elastomeric", "any"] = "any"
    chemical_resistance_preference: list[str] = Field(default_factory=list)


class Material(BaseModel):
    material_id: str
    name: str
    common_trade_names: list[str] = Field(default_factory=list)
    family: Literal["polymer", "metal", "elastomer", "composite"]
    category: str
    density_g_cm3: float = Field(gt=0)
    tensile_strength_mpa: float = Field(gt=0)
    yield_strength_mpa: float | None = None
    elastic_modulus_mpa: float = Field(gt=0)
    flexural_modulus_mpa: float | None = None
    elongation_at_break_pct: float | None = None
    shore_hardness: str | None = None
    temperature_min_c: float = -40.0
    temperature_max_c: float = 80.0
    manufacturing_methods: list[str]
    sterilization_compatibility: dict[str, str] = Field(
        default_factory=lambda: {
            "EtO": "Compatible",
            "Gamma": "Compatible",
            "Autoclave": "Not Recommended",
            "E-beam": "Compatible",
            "VHP": "Compatible"
        }
    )
    chemical_resistance: list[str] = Field(default_factory=list)
    iso_10993_biocompatibility_reference: str = "ISO 10993 compliant grades commercially available"
    typical_medical_applications: list[str] = Field(default_factory=list)
    source: str
    source_reference: str
    data_retrieval_date: str = "2026-01-01"


class CandidateScore(BaseModel):
    material: Material
    score: float = Field(ge=0.0, le=1.0)
    engineering_fit: Literal["Excellent", "Good", "Moderate", "Low"]
    matched_criteria: list[str] = Field(default_factory=list)
    unmatched_criteria: list[str] = Field(default_factory=list)
    sterilization_note: str = ""
    engineering_notes: str = ""
    evidence_provenance: str = ""
    regulatory_disclaimer: str = (
        "Engineering fit score only. Physical prototypes require independent bio-compatibility "
        "and sterilization validation testing per ISO 10993 / FDA guidelines."
    )
