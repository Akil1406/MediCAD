# Material Recommendation Engine

## Goal

Determine candidate materials that satisfy explicit engineering requirements.

Do not label a material clinically safe based only on an LLM recommendation.

## Material schema

```python
class Material(BaseModel):
    material_id: str
    name: str
    category: str
    density_g_cm3: float | None
    tensile_strength_mpa: float | None
    elastic_modulus_mpa: float | None
    temperature_min_c: float | None
    temperature_max_c: float | None
    manufacturing_methods: list[str]
    sterilization_notes: list[str]
    source: str
    source_date: str | None
```

## Ranking

Use deterministic scoring.

Example factors:

```text
+ manufacturing method matches
+ strength requirement satisfied
+ temperature requirement satisfied
+ flexibility requirement satisfied
+ dimensional stability requirement satisfied
```

Return reasons for every recommendation.

## Output

```json
{
  "material": "Candidate A",
  "score": 0.86,
  "matched_requirements": [
    "manufacturing_process",
    "minimum_strength"
  ],
  "unverified_requirements": [
    "clinical_application"
  ]
}
```

## Important distinction

Show three separate concepts:

```text
Engineering compatibility
Evidence/source quality
Clinical/regulatory status
```

Never collapse these into one "safe material" score.

## Data provenance

Every external material record should retain:

- source
- retrieval date
- material grade
- manufacturer
- revision/version

The UI should explain why each candidate was selected.
