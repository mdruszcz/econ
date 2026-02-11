"""Enums and type aliases for the ML2 model."""

from enum import Enum, auto
from typing import TypeAlias

Year: TypeAlias = int
VarName: TypeAlias = str


class VariableKind(Enum):
    EXOGENOUS = auto()
    PRE_RECURSIVE = auto()
    INTERDEPENDENT = auto()
    POST_RECURSIVE = auto()


class EquationType(Enum):
    IDENTITY = auto()
    BEHAVIORAL = auto()
    TECHNICAL = auto()


class ConvergenceStatus(Enum):
    CONVERGED = auto()
    MAX_ITERATIONS = auto()
    DIVERGED = auto()
