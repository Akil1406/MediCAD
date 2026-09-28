# MediCAD — Parametric Medical Device CAD & Engineering Platform

**MediCAD** is a full-stack, AI-orchestrated parametric CAD prototyping and engineering analysis assistant designed specifically for medical-tool concepts (catheters, micro-tubes, tapered introducers, ISO Luer connectors, syringe barrels, and plungers).

It bridges the gap between high-level clinical intent and deterministic, manufacturing-ready 3D CAD models, offering automated Level 1/2 design rule validation, ISO 10993-referenced material suitability scoring, and physics-based mechanical simulation.

---

## Table of Contents

- [What It Is](#what-it-is)
- [What It Does](#what-it-does)
- [Architecture & Tech Stack](#architecture--tech-stack)
- [Project Directory Structure](#project-directory-structure)
- [Getting Started & Running Locally](#getting-started--running-locally)
- [Supported Device Archetypes](#supported-device-archetypes)
- [Engineering Analysis & Simulation Solvers](#engineering-analysis--simulation-solvers)
- [Safety & Regulatory Boundaries](#safety--regulatory-boundaries)

---

## What It Is

MediCAD is an engineering prototyping assistant built with a **React/TypeScript frontend**, a **Python FastAPI backend**, a **LangChain/LangGraph agent architecture**, and a **deterministic parametric CAD geometry engine**. 

Instead of relying on an LLM to generate raw CAD code (which is prone to geometric hallucination and unconstrained execution), MediCAD uses the LLM solely as an intent interpreter and requirements orchestrator. All 3D geometry generation, engineering calculations, and validation checks are executed through deterministic Python services.

---

## What It Does

### 1. Natural-Language AI Design Intake
- Translate conversational clinical requirements (e.g., *"150 mm catheter shaft with 2.0 mm OD, 1.2 mm lumen, and a 5 mm atraumatic tip"*) into structured, type-checked parametric dimensions.
- Utilizes a bounded LangGraph revision cycle that enforces geometric sanity rules before CAD synthesis.

### 2. Interactive 3D CAD Studio & WebGL Viewport
- Real-time 3D visualization powered by **Three.js** with `OrbitControls`, `STLLoader`, dynamic studio lighting, coordinate grid toggles, wireframe inspection, and shader color selection.
- Real-time geometric HUD displaying calculated volume (`mm³`), surface area (`mm²`), French catheter scale (`Fr`), and bounding boxes.

### 3. Dynamic Parametric Workbench
- Intuitive sliders and numeric inputs for fine-tuning lengths, inner/outer diameters, tip bevel angles, barb counts, and flange dimensions.
- Sub-second deterministic solid mesh regeneration upon parameter adjustment.

### 4. Two-Level Engineering & Manufacturing Validation
- **Level 1 (Geometric Checks):** Wall thickness thresholds, inner vs. outer diameter consistency, aspect ratios, and solid manifoldness.
- **Level 2 (Manufacturing Design Rules):** Precision micro-extrusion limits, injection molding short-shot risks, and SLA additive manufacturing resin-trapping constraints.

### 5. Medical Materials Matrix & Provenance Engine
- Catalog of 10 real-world medical-grade polymers, elastomers, and alloys (Pebax 7233/3533, PTFE, Pellethane TPU, Medical PP, Polycarbonate Rx1805, PEEK-OPTIMA, Stainless Steel 316L, Nitinol, and Platinum-cured Silicone).
- Deterministic multi-factor ranking based on tensile strength, flexibility profile (flexible, semi-rigid, rigid), and sterilization compatibility (Ethylene Oxide, Gamma radiation, Autoclave steam, E-beam).
- Complete data provenance with ISO 10993 biocompatibility references and technical datasheet citations.

### 6. Deterministic Physics Solvers
- **Burst Pressure Solver (Lamé Formulation):** Calculates hoop and radial stresses under internal pressure against material yield limits to find theoretical burst pressures and safety factors.
- **Column Buckling Solver (Euler Formula):** Computes critical axial insertion push load (`N` and `gf`) to predict catheter buckling risks during vascular navigation.
- **Syringe Dispense Flow Solver (Hagen-Poiseuille):** Evaluates nozzle pressure drops, hydraulic resistance, and required thumb actuation force (`N` and `kgf`) across varying fluid viscosities and needle gauges (18G–30G).

### 7. Controlled Export Packages & Immutable Version History
- Every parameter modification creates an immutable, versioned revision stored in SQLite with full audit logs and delta diff comparator.
- Controlled export gateway offering authoritative **ISO 10303-21 STEP (`.step`)** CAD models, triangulated **STL (`.stl`)** meshes, JSON specifications, and complete **Markdown (`.md`)** engineering reports behind mandatory regulatory disclaimer confirmation gates.

---

## Architecture & Tech Stack

```text
React + TypeScript + Vite Frontend (Port 5173)
        │
        │ REST API (/api/v1/...)
        ▼
Python FastAPI Backend (Port 8000)
        │
        ├── LangChain + LangGraph Agent Pipeline (Intent Interpretation)
        │
        ├── Deterministic CAD Engine (CadQuery / Trimesh / SolidMesh)
        │
        ├── Level 1/2 Validation Rules (Geometry & Manufacturing Checks)
        │
        ├── Medical Materials Database (Catalog & Multi-Factor Ranker)
        │
        ├── Physical Simulation Solvers (Lamé / Euler / Hagen-Poiseuille)
        │
        └── SQLite Storage & Versioning (Immutable History & Audit Trail)
```

### Technology Breakdown

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, TypeScript, Vite, Three.js (`@types/three`), Lucide React, React Router v6 |
| **Backend** | Python 3.11+, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy, SQLite |
| **AI & Workflow** | LangChain Core, LangGraph (State Graph Engine) |
| **CAD & Math** | NumPy, SciPy, Trimesh, CadQuery concepts |
| **Testing** | Pytest, FastAPI TestClient, Vitest/tsc |

---

## Project Directory Structure

```text
MediCAD/
├── README.md                             # Global project documentation
├── medical_cad_builder_blueprint/        # System blueprints and architectural specifications
└── App/                                  # Complete full-stack application
    ├── backend/                          # FastAPI REST API
    │   ├── pyproject.toml
    │   └── app/
    │       ├── main.py                   # FastAPI application entrypoint
    │       ├── config.py                 # Server settings, CORS, and paths
    │       ├── api/routes/               # API endpoints (designs, cad, materials, simulations, exports, ai)
    │       ├── models/                   # Pydantic schemas (specs, validation, materials, simulation)
    │       ├── cad/                      # Parametric CAD generators & STEP/STL exporters
    │       ├── validation/               # Geometric & manufacturing design rules
    │       ├── materials/                # Medical materials database & ranking engine
    │       ├── simulation/               # Structural & fluid mechanical physics solvers
    │       ├── storage/                  # SQLite persistence & immutable versioning
    │       ├── reports/                  # Markdown prototyping report generator
    │       ├── tools/                    # LangChain tool bindings
    │       └── agents/                   # LangGraph orchestrator & state machine
    │
    ├── frontend/                         # React + TypeScript + Vite SPA
    │   ├── package.json
    │   ├── vite.config.ts
    │   ├── tsconfig.json
    │   ├── src/
    │   │   ├── components/               # ThreeViewer, ParameterForm, ValidationPanel, MaterialMatrix, etc.
    │   │   ├── pages/                    # DashboardPage, NewDesignPage, DesignStudioPage, VersionHistoryPage
    │   │   ├── services/                 # Typed API client services
    │   │   ├── types/                    # TypeScript interfaces matching backend schemas
    │   │   ├── App.tsx
    │   │   ├── main.tsx
    │   │   └── index.css                 # Design system stylesheet
    │
    ├── src/                              # Core CAD & engineering library modules
    ├── tests/                            # Automated pytest test suites
    ├── data/                             # SQLite database storage (`medcad.db`)
    └── exports/                          # Generated CAD export bundles
```

---

## Getting Started & Running Locally

### Prerequisites
- **Python:** Version 3.11 or higher
- **Node.js:** Version 18 or higher (with `npm`)

---

### Step 1: Start the Backend (FastAPI)

Open a terminal and navigate to the `App` directory:

```powershell
cd c:\Users\saleem\Downloads\MediCAD\App
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

- **Backend API:** `http://127.0.0.1:8000`
- **Interactive Swagger Docs:** [`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs)
- **Health Check Endpoint:** [`http://127.0.0.1:8000/health`](http://127.0.0.1:8000/health)

*(Note: If you run the command while inside `App\backend`, use `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload`)*

---

### Step 2: Start the Frontend (React + Vite)

Open a second terminal and navigate to the `App/frontend` directory:

```powershell
cd c:\Users\saleem\Downloads\MediCAD\App\frontend
npm install    # (First time only)
npm run dev
```

- **Web Application:** [`http://127.0.0.1:5173`](http://127.0.0.1:5173)

---

### Step 3: Run Automated Tests

To execute the backend test suite:

```powershell
cd c:\Users\saleem\Downloads\MediCAD\App
python -m pytest backend/tests/ -v
```

To verify the frontend TypeScript compilation and production build:

```powershell
cd c:\Users\saleem\Downloads\MediCAD\App\frontend
npm run build
```

---

## Supported Device Archetypes

1. **Vascular Catheter (`catheter`):** Main shaft OD/ID, length, distal tapered atraumatic tip length, tip curve/bevel angle, and proximal ISO Luer connection hub.
2. **Straight Micro-Tube (`tube`):** Thin-wall extruded hollow cylinders with customizable wall thickness and aspect ratios.
3. **Tapered Shaft (`tapered_tube`):** Smooth conical diameter transitions between proximal hub and distal tip.
4. **Luer Connector (`connector`):** ISO 594 / ISO 80369-7 standard 6% conical male/female Luer lock fittings with retention barbs.
5. **Syringe Injector Barrel (`injector`):** Main fluid cylinder bore, wall thickness, distal nozzle/needle hub, and finger grip flanges.
6. **Plunger Piston (`plunger`):** Sealing stopper head, elastomer rib count, structural central rod, and thumb press disc.
7. **Syringe Assembly (`assembly`):** Multi-body concentric fit with radial clearance calculation and interference detection.

---

## Engineering Analysis & Simulation Solvers

| Solver | Formula / Theory | Engineering Output |
|---|---|---|
| **Burst Pressure** | Lamé Equations for thick/thin cylinders | Radial stress, hoop stress, von Mises stress, yield safety factor, and burst pressure (`bar`). |
| **Column Buckling** | Euler Column Buckling Theory | Moment of inertia, critical buckling load (`N` & `gf`), and pushability safety factor. |
| **Syringe Flow** | Hagen-Poiseuille Viscous Flow | Orifice pressure drop, plunger hydraulic force, seal friction, and total operator thumb force (`N` & `kgf`). |

---

## Safety & Regulatory Boundaries

> [!IMPORTANT]
> **Regulatory Disclaimer:** MediCAD is strictly an **engineering design prototyping and computational feasibility assistant**. 
> - CAD geometries, material rankings, and simulation outputs are **not clinical advice**.
> - They do **not** constitute evidence of regulatory approval (FDA 510(k), PMA, or CE mark), clinical safety, sterility validation, biocompatibility certification, or readiness for in-vivo / patient use.
> - All physical prototypes must undergo independent physical testing and formal quality system verification (ISO 13485, ISO 10993, FDA 21 CFR Part 820) prior to any clinical application.
