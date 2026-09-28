# React Frontend Blueprint

## Stack
- React
- TypeScript
- Vite
- React Router
- Zustand if global state is needed
- Browser-based 3D mesh/CAD visualization

## Pages

```text
/                         Dashboard
/design/new               New Design Studio
/design/:designId         Design Studio
/design/:designId/history Version History
```

## Design Studio

```text
┌─────────────────────────────────────────────────────┐
│ Medical CAD Builder                                 │
├─────────────────────────────────────────────────────┤
│ Design Request                                      │
│ [ Describe your medical tool...                  ]  │
│                                      [Generate]      │
├──────────────────────┬──────────────────────────────┤
│ Parameters           │ CAD Preview                  │
│ Length [150.0]       │          3D model            │
│ OD     [2.0]         │                              │
│ ID     [1.2]         │                              │
│ Tip    [5.0]         │                              │
│ [Regenerate CAD]     │                              │
├──────────────────────┴──────────────────────────────┤
│ Validation                                           │
├─────────────────────────────────────────────────────┤
│ Materials                                            │
├─────────────────────────────────────────────────────┤
│ Simulation / Engineering Analysis                   │
├─────────────────────────────────────────────────────┤
│ [Export STEP] [Export STL] [Export Report]           │
└─────────────────────────────────────────────────────┘
```

## API Services

Create:

```text
src/services/api.ts
src/services/designs.ts
src/services/cad.ts
src/services/materials.ts
src/services/simulations.ts
```

Example:

```typescript
export async function createDesign(request: DesignRequest) {
  const response = await fetch("/api/v1/designs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error("Failed to create design");
  }

  return response.json();
}
```

## Parameter Editing

```text
React state
   ↓
PATCH /api/v1/designs/{id}/parameters
   ↓
FastAPI
   ↓
Pydantic validation
   ↓
CAD generation
   ↓
React viewer update
```

## CAD Viewer

Use a controlled endpoint such as:

```text
GET /api/v1/exports/{export_id}/preview
```

The browser must never access server filesystem paths.

For MVP, STL/mesh preview is sufficient. Exact STEP/BREP visualization can be added later.

## Loading States

```text
Generating specification...
Generating CAD...
Validating geometry...
Finding materials...
Complete
```

For expensive jobs, use polling/WebSockets.

## Export Approval

Before export:

> This design is an engineering prototype and has not been clinically or regulatorily validated.

Record the approval through FastAPI.
