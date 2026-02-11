"""Gauss-Seidel solver with 3-phase algorithm."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from ml2.equations.registry import EquationRegistry
from ml2.parameters import ML2Scalars
from ml2.state import SimulationState
from ml2.types import ConvergenceStatus, Year

logger = logging.getLogger(__name__)


@dataclass
class YearConvergence:
    year: Year
    iterations: int
    max_residual: float
    status: ConvergenceStatus


class GaussSeidelSolver:
    """Three-phase Gauss-Seidel solver for the ML2 model.

    Phase 1 (Pre-recursive): compute exogenous variables and instrument mappings.
    Phase 2 (Iterative): solve interdependent block with under-relaxation.
    Phase 3 (Post-recursive): compute derived ratios and diagnostics.

    Convergence criterion: max relative change < eps across all inter variables.
    Under-relaxation: new = relax * computed + (1 - relax) * old.
    """

    def __init__(
        self,
        registry: EquationRegistry,
        scalars: ML2Scalars,
        relaxation: float = 0.2,
        eps: float = 0.0001,
        max_iter: int = 1000,
    ) -> None:
        self._registry = registry
        self._scalars = scalars
        self._relaxation = relaxation
        self._eps = eps
        self._max_iter = max_iter

    def solve_year(self, state: SimulationState, t: Year) -> YearConvergence:
        """Solve all equations for a single year t."""
        # Phase 1: Pre-recursive
        for var in self._registry.pre_order:
            eq = self._registry.get(var)
            if eq is not None:
                val = eq.compute(state, t, self._scalars)
                state.set(var, t, val)

        # Phase 2: Iterative Gauss-Seidel
        status = ConvergenceStatus.MAX_ITERATIONS
        max_resid = 0.0
        iterations = 0

        for it in range(1, self._max_iter + 1):
            max_resid = 0.0
            for var in self._registry.inter_order:
                eq = self._registry.get(var)
                if eq is None:
                    continue

                old_val = state.get(var, t)
                new_val = eq.compute(state, t, self._scalars)

                # Under-relaxation
                relaxed = self._relaxation * new_val + (1 - self._relaxation) * old_val
                state.set(var, t, relaxed)

                # Relative residual
                if abs(old_val) > 1e-10:
                    resid = abs(relaxed - old_val) / abs(old_val)
                else:
                    resid = abs(relaxed - old_val)
                max_resid = max(max_resid, resid)

            iterations = it
            if max_resid < self._eps:
                status = ConvergenceStatus.CONVERGED
                break

        # Phase 3: Post-recursive
        for var in self._registry.post_order:
            eq = self._registry.get(var)
            if eq is not None:
                val = eq.compute(state, t, self._scalars)
                state.set(var, t, val)

        logger.debug(
            "Year %d: %d iterations, max residual=%.6f, status=%s",
            t, iterations, max_resid, status.name,
        )
        return YearConvergence(
            year=t,
            iterations=iterations,
            max_residual=max_resid,
            status=status,
        )

    def solve(self, state: SimulationState, sim_years: list[Year]) -> list[YearConvergence]:
        """Solve the model for all simulation years sequentially."""
        results = []
        for t in sim_years:
            conv = self.solve_year(state, t)
            results.append(conv)
        return results
