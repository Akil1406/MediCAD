# Safety, Quality, and Medical-Device Boundaries

## Required product boundary

A CAD model is an engineering artifact. It is not proof of medical-device safety, efficacy, sterility, biocompatibility, regulatory approval, or patient suitability.

## UI disclaimer

Display a concise notice such as:

> This software generates engineering design prototypes and analysis artifacts. Outputs are not clinical advice and are not evidence of safety, efficacy, biocompatibility, sterilization validation, regulatory approval, or suitability for patient use.

## Claims to avoid

Do not automatically state:

- FDA approved
- clinically safe
- safe for implantation
- safe for injection
- biocompatible
- sterile
- ready for patient use
- manufacturing-ready

## Engineering vs clinical outputs

The application can calculate or display:

```text
dimensions
volume
surface area
estimated mass
wall thickness
CAD topology
engineering material properties
simulation outputs
```

It should not infer from geometry alone:

```text
clinical efficacy
patient safety
clinical risk
sterility
biocompatibility
regulatory clearance
```

## Human review gates

Require review before:

1. final export
2. selecting a material for a physical prototype
3. interpreting simulation results
4. transferring a design to manufacturing

## Traceability

Record:

```text
user request
design version
parameters
derived parameters
CAD template version
material sources
validation rules
simulation configuration
approval event
```

A future production system should integrate appropriate design controls, risk management, verification/validation, manufacturing controls, quality systems, and regulatory workflows with qualified professionals.
