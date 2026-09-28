# Medical CAD Builder Blueprint

This folder contains the implementation instructions for a Python-based application that uses LangChain + LangGraph to orchestrate parametric CAD design workflows.

## Read in this order

1. `00_PROJECT_OVERVIEW.md`
2. `01_SYSTEM_ARCHITECTURE.md`
3. `02_DATA_MODELS_AND_SCHEMA.md`
4. `04_CAD_ENGINE_INSTRUCTIONS.md`
5. `03_LANGCHAIN_LANGGRAPH_AGENT.md`
6. `05_MATERIAL_ENGINE.md`
7. `06_SIMULATION_AND_VALIDATION.md`
8. `07_UI_AND_USER_WORKFLOW.md`
9. `08_IMPLEMENTATION_ROADMAP.md`
10. `09_CODING_STANDARDS_AND_TESTING.md`
11. `10_AGENT_SYSTEM_PROMPT.md`
12. `11_INITIAL_PROJECT_PROMPT.md`
13. `12_SAFETY_AND_MEDICAL_DEVICE_BOUNDARIES.md`

## Recommended development sequence

```text
Pydantic models
      ↓
Deterministic CAD templates
      ↓
Geometry validation
      ↓
STEP/STL export
      ↓
Streamlit UI
      ↓
Material database
      ↓
LangChain tools
      ↓
LangGraph workflow
      ↓
Simulation
      ↓
Traceability / quality controls
```

The key architecture principle is:

> The LLM controls workflow and interprets intent; deterministic Python/CAD tools remain the source of truth for geometry and engineering calculations.
