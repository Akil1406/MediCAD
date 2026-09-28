# Data Models and API Schema

Use Pydantic models as the backend source of truth.

## Design Request

```python
class DesignRequest(BaseModel):
    device_type: str
    purpose: str
    dimensions: dict[str, float] = {}
    units: str = "mm"
    material_requirements: list[str] = []
    manufacturing_method: str | None = None
    notes: str = ""
```

## Catheter

```python
class CatheterSpec(BaseModel):
    length_mm: float = Field(gt=0)
    outer_diameter_mm: float = Field(gt=0)
    inner_diameter_mm: float = Field(gt=0)
    tip_length_mm: float = Field(gt=0)
    tip_angle_deg: float = Field(default=0, ge=0, le=90)
    tolerance_mm: float = Field(default=0.05, gt=0)
```

Require:

```text
outer_diameter_mm > inner_diameter_mm
```

Wall thickness:

```text
wall = (outer_diameter_mm - inner_diameter_mm) / 2
```

## Injector

```python
class InjectorSpec(BaseModel):
    body_length_mm: float = Field(gt=0)
    body_outer_diameter_mm: float = Field(gt=0)
    internal_volume_ml: float = Field(gt=0)
    nozzle_length_mm: float = Field(gt=0)
    nozzle_outer_diameter_mm: float = Field(gt=0)
    nozzle_inner_diameter_mm: float = Field(gt=0)
    plunger_length_mm: float = Field(gt=0)
```

## Materials

```python
class MaterialRequirements(BaseModel):
    minimum_strength_mpa: float | None = None
    maximum_temperature_c: float | None = None
    flexibility: str | None = None
    manufacturing_process: str | None = None
    sterilization_method: str | None = None
```

## API Response

```python
class DesignResponse(BaseModel):
    design_id: str
    version_id: str
    status: str
    specification: dict
    validation: dict
    cad: dict | None
    materials: list[dict]
```

## CAD Response

```python
class CadResponse(BaseModel):
    status: str
    step_url: str | None
    stl_url: str | None
    preview_url: str | None
    volume_mm3: float | None
    bounding_box_mm: dict | None
```

Use controlled API URLs, never raw server paths.

## LangGraph State

```python
class DesignState(TypedDict, total=False):
    user_request: str
    specification: dict
    selected_template: str
    cad_result: dict
    geometry_checks: dict
    material_candidates: list[dict]
    report: str
    errors: list[str]
    revision_count: int
```
