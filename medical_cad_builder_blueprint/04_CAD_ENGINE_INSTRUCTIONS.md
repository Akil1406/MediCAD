# CAD Engine Instructions

## Recommended CAD engine

Use CadQuery as the primary Python CAD library.

Use STEP as the authoritative CAD interchange format and STL mainly for visualization/prototyping.

## Directory

```text
src/medcad/cad/
├── base.py
├── tube.py
├── catheter.py
├── injector.py
├── connector.py
└── exporters.py
```

## Tube example

```python
def build_tube(spec):
    outer = (
        cq.Workplane("XY")
        .circle(spec.outer_diameter_mm / 2)
        .extrude(spec.length_mm)
    )

    inner = (
        cq.Workplane("XY")
        .circle(spec.inner_diameter_mm / 2)
        .extrude(spec.length_mm)
    )

    return outer.cut(inner)
```

## Parameterization

Never hard-code design dimensions inside a template.

Use validated specification fields:

```text
spec.length_mm
spec.outer_diameter_mm
spec.inner_diameter_mm
```

## Derived dimensions

Calculate derived quantities in Python.

Example:

```python
wall_mm = (outer_diameter_mm - inner_diameter_mm) / 2
```

The LLM may explain the calculation, but the deterministic code is authoritative.

## CAD validation

After generation, check:

- model exists
- expected solid count
- bounding box
- volume
- wall thickness
- holes/openings
- topology validity where supported
- component interference for assemblies

## Assemblies

Later support:

```text
components/
├── catheter_tube
├── hub
├── connector
└── cap
```

Represent assemblies as structured components plus transforms.

## Export

Implement:

```python
def export_step(model, path):
    cq.exporters.export(model, path)
```

Also support STL and JSON specification export.

Recommended version artifact:

```text
design.json
model.step
preview.stl
validation.json
report.md
```
