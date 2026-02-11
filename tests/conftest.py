"""Shared test fixtures."""

import pytest

from ml2.engine import SimulationEngine
from ml2.equations.registry import EquationRegistry
from ml2.parameters import ML2Scalars
from ml2.solver import GaussSeidelSolver
from ml2.variables import BaselineDataLoader


@pytest.fixture
def scalars():
    return ML2Scalars()


@pytest.fixture
def registry():
    return EquationRegistry()


@pytest.fixture
def baseline_state(engine):
    """Get baseline state from the engine (which ensures all variables exist)."""
    return engine.baseline.copy()


@pytest.fixture
def solver(registry, scalars):
    return GaussSeidelSolver(registry, scalars)


@pytest.fixture
def engine():
    eng = SimulationEngine()
    eng.load_baseline()
    return eng
