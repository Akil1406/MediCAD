# LangChain + LangGraph Agent Instructions

## Objective

Use LangChain and LangGraph to translate natural-language requests into structured CAD specifications and invoke deterministic engineering tools.

The agent is the orchestrator, not the CAD engine.

## Tools

Create narrow Python tools:

```python
from langchain_core.tools import tool

@tool
def validate_device_spec(spec_json: str) -> str:
    """Validate a device specification against its Pydantic model."""
    ...

@tool
def generate_device_cad(device_type: str, spec_json: str) -> str:
    """Generate a registered parametric CAD template."""
    ...

@tool
def search_materials(requirements_json: str) -> str:
    """Return material candidates matching explicit requirements."""
    ...

@tool
def run_geometry_checks(cad_path: str, spec_json: str) -> str:
    """Run deterministic geometry/design-rule checks."""
    ...
```

## Graph nodes

### `extract_requirements`

Convert the user request into structured output.

Do not invent critical dimensions.

### `validate_specification`

Run Pydantic validation.

If required information is missing, ask the user rather than silently guessing.

### `select_template`

Map a validated device type to a registered template.

```python
TEMPLATES = {
    "tube": build_tube,
    "catheter": build_catheter,
    "injector": build_injector,
}
```

### `generate_cad`

Call the selected deterministic function.

### `run_geometry_checks`

Run deterministic checks.

If critical errors exist, send the state to a bounded revision node.

### `evaluate_materials`

Use the material database and deterministic filtering/ranking.

### `generate_report`

Include:

- design parameters
- derived dimensions
- material candidates
- warnings
- validation status
- export information

### `human_approval`

Require explicit user approval before final export.

## Revision loop

```text
generate_cad
    ↓
validate_geometry
    ├── error → revise_spec → generate_cad
    └── pass → materials
```

Set a maximum of 2–3 automatic revisions.

## LangChain responsibilities

Use LangChain for:

- model integration
- structured output
- tool definitions
- prompt templates
- messages

Use LangGraph for:

- state
- workflow branching
- retries
- revision loops
- human approval
- persistence

## Agent rules

The system prompt should require:

- no unsupported clinical claims
- no arbitrary code execution
- no fabricated material properties
- no unit ambiguity
- tools for calculations
- registered CAD templates only
- explicit assumptions
- uncertainty/warnings when appropriate
