"""FastAPI route for LangGraph agent orchestration."""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from ...agents import run_design_pipeline


router = APIRouter(prefix="/ai", tags=["AI Agent"])


class AgentPromptRequest(BaseModel):
    prompt: str = Field(description="Natural language design intent")


@router.post("/agent")
def run_agent_workflow(payload: AgentPromptRequest):
    """Execute LangGraph agent workflow to translate text into verified CAD."""
    final_state = run_design_pipeline(payload.prompt)
    return {
        "status": final_state.get("status", "COMPLETED"),
        "target_device_type": final_state.get("target_device_type"),
        "specification": final_state.get("specification"),
        "cad_result": final_state.get("cad_result"),
        "geometry_checks": final_state.get("geometry_checks"),
        "material_candidates": final_state.get("material_candidates"),
        "engineering_report": final_state.get("engineering_report")
    }
