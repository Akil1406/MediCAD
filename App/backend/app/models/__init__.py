"""Backend models package."""

from .base import BaseSpec, BoundingBox
from .specs import (
    TubeSpec, CatheterSpec, TaperedTubeSpec,
    ConnectorSpec, InjectorSpec, PlungerSpec, AssemblySpec,
    DesignCreateRequest, ParameterUpdateRequest
)
from .validation import SeverityLevel, ValidationIssue, ValidationReport
from .materials import Material, MaterialRequirements, CandidateScore
from .simulation import (
    SimulationConfigRequest,
    BurstSimulationResult,
    BucklingSimulationResult,
    DispenseSimulationResult
)

__all__ = [
    "BaseSpec",
    "BoundingBox",
    "TubeSpec",
    "CatheterSpec",
    "TaperedTubeSpec",
    "ConnectorSpec",
    "InjectorSpec",
    "PlungerSpec",
    "AssemblySpec",
    "DesignCreateRequest",
    "ParameterUpdateRequest",
    "SeverityLevel",
    "ValidationIssue",
    "ValidationReport",
    "Material",
    "MaterialRequirements",
    "CandidateScore",
    "SimulationConfigRequest",
    "BurstSimulationResult",
    "BucklingSimulationResult",
    "DispenseSimulationResult"
]
