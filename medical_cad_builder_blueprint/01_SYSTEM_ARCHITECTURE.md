# System Architecture — React + FastAPI

## React Frontend

React handles:
- natural-language design input
- device selection
- parameter editing
- 3D CAD/mesh preview
- validation results
- material candidates
- simulation results
- design history
- export controls
- approval UI

Suggested structure:

```text
frontend/src/
├── components/
│   ├── DesignPrompt/
│   ├── ParameterEditor/
│   ├── CadViewer/
│   ├── ValidationPanel/
│   ├── MaterialTable/
│   ├── SimulationPanel/
│   └── ExportPanel/
├── pages/
├── hooks/
├── services/
│   ├── api.ts
│   ├── designs.ts
│   ├── cad.ts
│   ├── materials.ts
│   └── simulations.ts
├── stores/
├── types/
├── App.tsx
└── main.tsx
```

## FastAPI Backend

FastAPI is the application's API boundary.

Responsibilities:
- REST API
- request validation
- invoking LangGraph
- invoking CAD services
- materials
- validation
- simulations
- exports
- database persistence
- job status

Suggested structure:

```text
backend/app/
├── main.py
├── api/
│   └── routes/
│       ├── designs.py
│       ├── cad.py
│       ├── materials.py
│       ├── simulations.py
│       └── exports.py
├── agents/
├── cad/
├── models/
├── materials/
├── simulation/
├── validation/
├── reports/
├── storage/
└── tools/
```

## Request Flow

```text
React
  ↓ POST /api/v1/designs
FastAPI
  ↓
LangGraph
  ↓
Pydantic specification
  ↓
CAD service
  ↓
STEP/STL
  ↓
FastAPI
  ↓
React viewer
```

## Database

Use SQLAlchemy.

MVP:
```text
SQLite
```

Later:
```text
PostgreSQL
```

Recommended entities:
```text
users
designs
design_versions
device_specs
materials
material_sources
validation_results
simulation_runs
exports
audit_events
```

## File Storage

Never accept arbitrary paths from React.

```text
exports/{design_id}/{version_id}/
├── model.step
├── preview.stl
├── design.json
├── validation.json
└── report.md
```

Expose files only through controlled FastAPI endpoints.

## Long-Running Jobs

```text
React → FastAPI → Queue → Worker → CAD/FEA/CFD
                                  ↓
                           Database + Files
```

Use polling initially; add WebSockets when needed.

## Security

Prevent:
- arbitrary code execution
- path traversal
- arbitrary filesystem access
- unauthorized file access
- exposed LLM credentials
- unrestricted agent tools

Configure production CORS with explicit frontend origins.
