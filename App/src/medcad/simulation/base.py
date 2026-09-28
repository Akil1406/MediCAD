"""Simulator abstract interface."""

from abc import ABC, abstractmethod
from typing import Any
from ..models.simulation import SimulationConfig


class BaseSimulator(ABC):
    """Abstract base class for all deterministic engineering simulation solvers."""

    @abstractmethod
    def run(self, spec: Any, config: SimulationConfig) -> Any:
        """Execute physical solver simulation."""
        pass
