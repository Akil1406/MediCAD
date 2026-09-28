"""MediCAD Models Package."""

from .base import BaseSpec, BoundingBox
from .specs import (
    TubeSpec,
    CatheterSpec,
    TaperedTubeSpec,
    ConnectorSpec,
    InjectorSpec,
    PlungerSpec,
    AssemblySpec,
    DesignRequest,
)
from .validation import (
    SeverityLevel,
    ValidationIssue,
    ValidationReport,
)
from .materials import (
    Material,
    MaterialRequirements,
    CandidateScore,
)
from .simulation import (
    SimulationConfig,
    BurstSimulationResult,
    BucklingSimulationResult,
    DispenseSimulationResult,
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
    "DesignRequest",
    "SeverityLevel",
    "ValidationIssue",
    "ValidationReport",
    "Material",
    "MaterialRequirements",
    "CandidateScore",
    "SimulationConfig",
    "BurstSimulationResult",
    "BucklingSimulationResult",
    "DispenseSimulationResult",
]
