# Simulation and Engineering Validation

## Three levels

### Level 1 — Geometric validation

MVP:

- dimensions
- wall thickness
- volume
- surface area
- clearances
- intersections
- topology

### Level 2 — Engineering simulation

Later:

- structural stress
- deformation
- thermal analysis
- pressure/flow
- fatigue
- buckling

### Level 3 — Medical-device verification/validation

This is outside the scope of an AI/CAD prototype and requires qualified engineering, testing, quality, risk-management, and regulatory processes.

## Simulator interface

Create an abstraction:

```python
class Simulator:
    def run(self, model_path: str, parameters: dict) -> dict:
        raise NotImplementedError
```

Potential later backends include a structural FEA solver and a CFD solver.

## Structural simulation workflow

```text
CAD geometry
    ↓
mesh
    ↓
material properties
    ↓
boundary conditions
    ↓
loads
    ↓
solver
    ↓
results
    ↓
report
```

Do not allow the LLM to silently invent physically meaningful boundary conditions.

## Result metadata

Store:

```text
solver
solver_version
mesh information
material properties
boundary conditions
loads
assumptions
convergence information
timestamp
```

## UI language

Use:

```text
SIMULATION RESULT
ENGINEERING CHECK
DESIGN WARNING
REQUIRES PROFESSIONAL REVIEW
```

Avoid:

```text
SAFE FOR PATIENT USE
APPROVED
CLINICALLY VALIDATED
READY FOR MANUFACTURING
```
