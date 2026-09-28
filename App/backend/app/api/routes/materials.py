"""FastAPI routes for medical materials catalog and multi-factor ranking."""

from fastapi import APIRouter, HTTPException
from ...models.materials import MaterialRequirements
from ...materials import MaterialDatabase, evaluate_and_rank_materials


router = APIRouter(prefix="/materials", tags=["Materials"])
db = MaterialDatabase()


@router.get("")
def list_materials():
    """List all registered medical-grade materials."""
    return {"materials": [m.model_dump() for m in db.get_all_materials()]}


@router.post("/rank")
def rank_materials(requirements: MaterialRequirements):
    """Deterministic multi-factor ranking against explicit engineering requirements."""
    ranked = evaluate_and_rank_materials(requirements, db=db)
    return {"candidates": [c.model_dump() for c in ranked]}


@router.get("/{material_id}")
def get_material_detail(material_id: str):
    """Fetch single material record by ID."""
    mat = db.get_material_by_id(material_id)
    if not mat:
        raise HTTPException(status_code=404, detail=f"Material '{material_id}' not found.")
    return {"material": mat.model_dump()}
