"""Abstract equation base class."""

import math
from abc import ABC, abstractmethod

from ml2.parameters import ML2Scalars
from ml2.state import SimulationState
from ml2.types import EquationType, VarName, Year


def safe_exp(x: float, limit: float = 0.5) -> float:
    """Clamped exponential to prevent overflow during iterative solving."""
    x = max(-limit, min(limit, x))
    return math.exp(x)


class Equation(ABC):
    """Base class for all ML2 model equations."""

    @property
    @abstractmethod
    def name(self) -> VarName:
        """Target variable name (e.g. 'GDP_')."""

    @property
    @abstractmethod
    def equation_type(self) -> EquationType:
        """Type of equation (IDENTITY, BEHAVIORAL, TECHNICAL)."""

    @property
    @abstractmethod
    def depends_on(self) -> list[VarName]:
        """Variables this equation reads (for dependency graph)."""

    @abstractmethod
    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        """Compute the target variable value for year t."""
