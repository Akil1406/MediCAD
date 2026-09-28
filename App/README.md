# MediCAD — Medical Tool CAD Prototyping & Engineering Studio

MediCAD is a parametric CAD prototyping assistant and engineering analysis application for medical-tool concepts such as tubes, catheters, connectors, and syringe components. It integrates typed Pydantic models, deterministic parametric 3D CAD modeling, multi-level geometric and manufacturing validation, an ISO-referenced medical materials database, engineering simulation solvers, SQLite immutable versioning, and a LangChain + LangGraph orchestrator with an interactive 3D Streamlit Studio.

---

## ⚠️ Medical Device & Safety Boundary Notice

> **IMPORTANT:** MediCAD is an engineering design prototyping aid and analysis assistant. Outputs are preliminary engineering artifacts and **do not constitute clinical advice, biocompatibility certification, sterilization validation, regulatory clearance (FDA/CE), or suitability for human patient use**.

---

## Key Features

1. **Deterministic Parametric CAD Engine**:
   - **Tube**: Hollow cylindrical extrusion with exact bore and wall thickness.
   - **Catheter**: Multi-segment catheter shaft with atraumatic tapered/beveled tip and proximal luer hub.
   - **Tapered Tube**: Conical transition shaft for dilators and introducers.
   - **Connector**: ISO 594 / ISO 80369 compatible male/female luer lock and hose barb fittings.
   - **Injector**: Syringe barrel body with finger flange, graduated cylinder, and luer nozzle.
   - **Plunger**: Syringe plunger rod with thumb pad and elastomeric seal ribs.
   - **Assembly**: Mated multi-component assemblies with clearance and interference analysis.
   - **Authoritative Exporters**: ISO 10303-21 STEP, binary/ASCII STL, Wavefront OBJ, and JSON specification manifests.

2. **Multi-Level Engineering & Geometric Validation**:
   - **Level 1 (Geometric Integrity)**: Inner vs. outer diameter consistency, minimum wall thickness, positive bounds, high aspect ratio buckling alerts, watertight manifold mesh checks.
   - **Level 2 (Manufacturing Constraints)**: Micro-extrusion limits, injection molding draft & short-shot warnings, and 3D printing micro-channel resolution checks.

3. **Medical Materials Engine**:
   - Curated catalog of medical-grade engineering polymers (Pebax 7233, Pebax 3533, PTFE, TPU Pellethane, Medical PP, Polycarbonate Makrolon Rx, PEEK Optima), metals (Surgical Stainless Steel 316L, Nitinol ASTM F2063), and elastomers (Medical Silicone LSR 4350).
   - Multi-factor deterministic scoring and ranking with sterilization compatibility matrices (EtO, Gamma, Autoclave, E-beam, VHP) and ISO 10993 provenance citations.

4. **Engineering Simulation Solvers**:
   - **Burst Pressure Solver**: Lamé thick-walled elastic cylinder formulations for hoop stress, radial stress, and yield safety factor.
   - **Euler Column Buckling Solver**: Critical axial load ($P_{cr}$) and pushability safety factor for catheter insertion.
   - **Syringe Flow Dynamics Solver**: Hagen-Poiseuille viscous pressure drop and plunger actuation force evaluation.

5. **SQLite Storage & Immutable Version Control**:
   - Immutable version records created on every parameter change.
   - Key-by-key parameter diff calculation and audit history logging.

6. **LangChain & LangGraph Orchestration**:
   - Narrow deterministic tool interfaces (`validate_device_spec`, `generate_device_cad`, `search_materials`, `run_geometry_checks`).
   - LangGraph state machine with automatic bounded revision loop (max 2 iterations).

7. **Interactive 3D Web Studio (`app.py`)**:
   - Natural language AI Concept Studio.
   - Parametric Workbench with real-time feedback.
   - Three.js 3D Viewport with solid, wireframe, and orbit controls.
   - Real-time Validation and Rules Dashboard.
   - Material Radar/Comparison Matrix.
   - Simulation Studio with interactive charts.
   - Version History Diff Viewer.
   - Controlled Export Package Download (STEP, STL, JSON, Report).

---

## Installation & Setup

### Prerequisites
- Python 3.11+

### Install Dependencies
```powershell
pip install -r requirements.txt
# or
pip install pydantic numpy scipy trimesh streamlit langchain langchain-core langgraph pandas pytest
```

### Launch the Streamlit Studio
```powershell
streamlit run app.py
```

### Run the Test Suite
```powershell
python -m pytest -v
```

---

## Repository Structure

```text
MediCAD/
├── app.py                         # Streamlit Interactive Web Application & 3D Studio
├── pyproject.toml                 # Package definition and dependencies
├── .env.example                   # Environment configuration
├── README.md                      # Documentation
├── src/
│   └── medcad/
│       ├── __init__.py
│       ├── config.py              # Global settings, paths, tolerances
│       ├── models/                # Pydantic typed specifications
│       │   ├── base.py
│       │   ├── specs.py           # Tube, Catheter, TaperedTube, Connector, Injector, Plunger
│       │   ├── validation.py      # ValidationIssue, ValidationReport, Severity
│       │   ├── materials.py       # Material, MaterialRequirements, CandidateScore
│       │   └── simulation.py      # SimulationConfig, SimulationResult models
│       ├── cad/                   # Deterministic parametric CAD templates
│       │   ├── base.py            # SolidMesh, CADResult, cylinder mesh primitives
│       │   ├── tube.py
│       │   ├── catheter.py
│       │   ├── tapered_tube.py
│       │   ├── connector.py
│       │   ├── injector.py
│       │   ├── plunger.py
│       │   ├── assembly.py
│       │   └── exporters.py       # STEP, STL, OBJ, and package manifest exporters
│       ├── validation/            # Geometry and engineering design rules
│       │   ├── geometry.py        # Level 1 geometry checks
│       │   └── design_rules.py    # Level 2 manufacturing design rules
│       ├── materials/             # Medical material database and ranking
│       │   ├── catalog.py         # Curated medical material dataset
│       │   ├── database.py        # SQLite storage with provenance
│       │   └── ranker.py          # Deterministic multi-factor scoring
│       ├── simulation/            # Engineering simulation calculators
│       │   ├── base.py
│       │   ├── burst_pressure.py  # Lamé burst & hoop stress
│       │   ├── buckling.py        # Euler column buckling
│       │   └── syringe_flow.py    # Hagen-Poiseuille dispense force
│       ├── storage/               # SQLite persistence and versioning
│       │   ├── db.py
│       │   └── versioning.py      # Version comparator and diffs
│       ├── reports/               # Engineering summary report generator
│       │   └── generator.py
│       ├── tools/                 # LangChain tool interfaces
│       │   └── cad_tools.py
│       └── agents/                # LangGraph state machine & orchestrator
│           ├── state.py
│           ├── prompts.py
│           └── orchestrator.py
├── data/
│   └── medcad.db                  # Local SQLite database
├── exports/                       # Controlled design export artifacts
└── tests/                         # Full Pytest test suite
    ├── test_specs.py
    ├── test_cad_templates.py
    ├── test_validation.py
    ├── test_materials.py
    ├── test_simulation.py
    ├── test_storage.py
    └── test_agent.py
```
