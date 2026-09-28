# Full-Stack Implementation Roadmap

## Phase 1 — FastAPI + CAD Core
- [ ] FastAPI project
- [ ] Pydantic models
- [ ] CadQuery
- [ ] Tube template
- [ ] Catheter template
- [ ] Injector body template
- [ ] Geometry validation
- [ ] STEP/STL export
- [ ] Backend tests

## Phase 2 — React Frontend
- [ ] Vite React TypeScript project
- [ ] Routing
- [ ] API client
- [ ] Dashboard
- [ ] Design Studio
- [ ] Parameter editor
- [ ] 3D viewer
- [ ] Validation panel
- [ ] Materials panel
- [ ] Export panel

## Phase 3 — React/FastAPI Integration
- [ ] OpenAPI contracts
- [ ] Design creation
- [ ] Parameter updates
- [ ] CAD generation
- [ ] Validation
- [ ] Materials
- [ ] Exports
- [ ] Loading/error states
- [ ] CORS

## Phase 4 — LangChain
- [ ] LLM abstraction
- [ ] Structured output
- [ ] Requirement extraction
- [ ] CAD tool
- [ ] Validation tool
- [ ] Material search tool

## Phase 5 — LangGraph
- [ ] Typed graph state
- [ ] Requirement extraction
- [ ] Specification validation
- [ ] CAD template selection
- [ ] CAD generation
- [ ] Geometry validation
- [ ] Bounded revision loop
- [ ] Material evaluation
- [ ] Report generation
- [ ] Human approval

## Phase 6 — Database
- [ ] SQLAlchemy
- [ ] SQLite
- [ ] Design persistence
- [ ] Versioning
- [ ] Material database
- [ ] Validation records
- [ ] Export records
- [ ] Audit events

## Phase 7 — Background Jobs

```text
FastAPI → Queue → Worker → CAD/FEA/CFD
```

Add job status endpoints and React polling/WebSocket support.

## Phase 8 — Simulation
- [ ] Simulator interface
- [ ] Structural simulation
- [ ] Mesh generation
- [ ] Simulation configuration
- [ ] Results parsing
- [ ] Results visualization

## Phase 9 — Production
- [ ] PostgreSQL
- [ ] Authentication
- [ ] Authorization
- [ ] Object/file storage
- [ ] Docker
- [ ] CI/CD
- [ ] Observability
- [ ] Security testing
- [ ] CAD regression testing
- [ ] Audit logging
