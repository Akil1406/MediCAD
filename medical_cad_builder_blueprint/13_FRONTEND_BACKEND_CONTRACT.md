# Frontend ↔ FastAPI Contract

React communicates with the Python application exclusively through FastAPI.

## Create Design

```http
POST /api/v1/designs
Content-Type: application/json
```

Example:

```json
{
  "device_type": "catheter",
  "purpose": "engineering prototype",
  "dimensions": {
    "length_mm": 150,
    "outer_diameter_mm": 2,
    "inner_diameter_mm": 1.2
  },
  "units": "mm"
}
```

## Parameter Update

```http
PATCH /api/v1/designs/{design_id}/parameters
```

FastAPI should:
1. validate input
2. create a new design version
3. regenerate deterministic CAD
4. run validation
5. return the new version

## CAD/Export Endpoints

```http
GET /api/v1/exports/{export_id}/step
GET /api/v1/exports/{export_id}/stl
GET /api/v1/exports/{export_id}/preview
GET /api/v1/exports/{export_id}/report
```

Use authorization before returning files.

## Simulation Jobs

```http
POST /api/v1/simulations
GET  /api/v1/jobs/{job_id}
```

Example:

```json
{
  "job_id": "job_123",
  "status": "running",
  "progress": 65
}
```

## OpenAPI

Use FastAPI's OpenAPI schema to keep TypeScript types synchronized with Pydantic models.

## Error Format

```json
{
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "Inner diameter must be smaller than outer diameter.",
    "field": "inner_diameter_mm"
  }
}
```

Never return Python stack traces to React.
