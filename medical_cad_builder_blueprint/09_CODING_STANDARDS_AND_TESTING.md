# Coding Standards and Testing

## Python standards

Use:

- Python 3.12+ if supported by the selected dependency versions
- type hints
- Pydantic
- pytest
- ruff
- clear module boundaries
- docstrings for public functions

## Unit tests

Test every CAD template.

```python
def test_catheter_dimensions():
    spec = CatheterSpec(
        length_mm=100,
        outer_diameter_mm=2,
        inner_diameter_mm=1
    )

    model = build_catheter(spec)

    assert model is not None
```

## Invalid parameter tests

Test:

```text
ID >= OD
negative length
zero diameter
negative tolerance
invalid tip angle
```

Every invalid case should fail predictably.

## CAD regression tests

Prefer expected geometric properties over visual-only comparison:

```text
bounding box
volume
surface area
solid count
```

## Agent tests

Mock the LLM.

Test:

```text
natural language
→ structured specification
→ validation
→ CAD tool
→ material tool
→ report
```

Live-LLM tests should be separate integration tests.

## Prompt regression tests

Maintain representative prompts such as:

```text
Create a 150 mm catheter with a 2 mm outer diameter and
1.2 mm inner diameter.

Create an injector body with a 5 mL target volume.

Make the tube longer.

Reduce the wall thickness.
```

Verify that outputs remain valid structured specifications.

## Security tests

Verify that user prompts cannot:

- execute shell commands
- inject Python into tool arguments
- overwrite arbitrary files
- access environment secrets
- escape the export directory

## Logging

Log:

```text
design_id
version
workflow_node
tool_name
success/failure
duration
error_code
```

Never log API keys.
