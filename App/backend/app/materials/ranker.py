"""Deterministic multi-factor material evaluation and ranking engine."""

from ..models.materials import Material, MaterialRequirements, CandidateScore
from .database import MaterialDatabase


def evaluate_and_rank_materials(
    requirements: MaterialRequirements,
    materials: list[Material] | None = None,
    db: MaterialDatabase | None = None
) -> list[CandidateScore]:
    if materials is None:
        db = db or MaterialDatabase()
        materials = db.get_all_materials()

    scored_candidates: list[CandidateScore] = []

    for mat in materials:
        score = 0.0
        max_possible_weight = 0.0
        matched = []
        unmatched = []
        notes = []

        if requirements.minimum_tensile_strength_mpa is not None:
            max_possible_weight += 25.0
            if mat.tensile_strength_mpa >= requirements.minimum_tensile_strength_mpa:
                score += 25.0
                matched.append(f"Tensile strength ({mat.tensile_strength_mpa:.1f} MPa >= {requirements.minimum_tensile_strength_mpa:.1f} MPa)")
            else:
                unmatched.append(f"Tensile strength ({mat.tensile_strength_mpa:.1f} MPa < {requirements.minimum_tensile_strength_mpa:.1f} MPa)")
        else:
            score += 15.0
            max_possible_weight += 15.0

        if requirements.flexibility_preference != "any":
            max_possible_weight += 25.0
            pref = requirements.flexibility_preference
            if pref == "rigid" and mat.elastic_modulus_mpa >= 1000.0:
                score += 25.0
                matched.append(f"Rigid modulus profile (E = {mat.elastic_modulus_mpa:.0f} MPa)")
            elif pref == "semi_rigid" and (200.0 <= mat.elastic_modulus_mpa <= 1500.0):
                score += 25.0
                matched.append(f"Semi-rigid flex modulus (E = {mat.elastic_modulus_mpa:.0f} MPa)")
            elif pref == "flexible" and (15.0 <= mat.elastic_modulus_mpa < 200.0):
                score += 25.0
                matched.append(f"Flexible catheter shaft grade (E = {mat.elastic_modulus_mpa:.0f} MPa)")
            elif pref == "elastomeric" and (mat.family == "elastomer" or mat.elastic_modulus_mpa < 15.0):
                score += 25.0
                matched.append(f"Elastomeric high elongation grade (E = {mat.elastic_modulus_mpa:.1f} MPa)")
            else:
                unmatched.append(f"Modulus ({mat.elastic_modulus_mpa:.0f} MPa) does not match '{pref}' target")
        else:
            score += 15.0
            max_possible_weight += 15.0

        if requirements.preferred_manufacturing_method:
            max_possible_weight += 20.0
            req_mfg = requirements.preferred_manufacturing_method.lower()
            if any(req_mfg in m.lower() for m in mat.manufacturing_methods):
                score += 20.0
                matched.append(f"Compatible with {requirements.preferred_manufacturing_method}")
            else:
                unmatched.append(f"Not standard for {requirements.preferred_manufacturing_method}")
        else:
            score += 15.0
            max_possible_weight += 15.0

        if requirements.required_sterilization_method:
            max_possible_weight += 20.0
            s_req = requirements.required_sterilization_method
            steril_map = {k.lower(): v for k, v in mat.sterilization_compatibility.items()}
            status = steril_map.get(s_req.lower(), "Unknown")
            if "compatible" in status.lower() and "not" not in status.lower():
                score += 20.0
                matched.append(f"{s_req} sterilization verified ({status})")
            else:
                unmatched.append(f"{s_req} sterilization is {status}")
                notes.append(f"Sterilization caveat: {s_req} is {status}")
        else:
            score += 15.0
            max_possible_weight += 15.0

        if requirements.max_operating_temp_c is not None:
            max_possible_weight += 10.0
            if mat.temperature_max_c >= requirements.max_operating_temp_c:
                score += 10.0
                matched.append(f"Thermal limit ({mat.temperature_max_c}°C >= {requirements.max_operating_temp_c}°C)")
            else:
                unmatched.append(f"Max temp ({mat.temperature_max_c}°C < {requirements.max_operating_temp_c}°C)")
        else:
            score += 10.0
            max_possible_weight += 10.0

        normalized_score = round(min(1.0, max(0.0, score / max_possible_weight)), 2)

        if normalized_score >= 0.85:
            fit_tier = "Excellent"
        elif normalized_score >= 0.70:
            fit_tier = "Good"
        elif normalized_score >= 0.50:
            fit_tier = "Moderate"
        else:
            fit_tier = "Low"

        steril_summary = "; ".join(f"{k}: {v}" for k, v in mat.sterilization_compatibility.items())
        provenance = f"Source: {mat.source} ({mat.source_reference}), Retrieved: {mat.data_retrieval_date}"

        candidate = CandidateScore(
            material=mat,
            score=normalized_score,
            engineering_fit=fit_tier,
            matched_criteria=matched,
            unmatched_criteria=unmatched,
            sterilization_note=steril_summary,
            engineering_notes=" | ".join(notes) if notes else "Engineering properties aligned with nominal criteria.",
            evidence_provenance=provenance
        )
        scored_candidates.append(candidate)

    scored_candidates.sort(key=lambda c: (c.score, c.material.tensile_strength_mpa), reverse=True)
    return scored_candidates
