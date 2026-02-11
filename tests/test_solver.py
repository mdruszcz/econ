"""Tests for the Gauss-Seidel solver."""

from ml2.types import ConvergenceStatus


class TestSolverConvergence:
    def test_solver_converges_on_baseline(self, solver, baseline_state):
        """Solver should converge for every year on the baseline."""
        sim_years = baseline_state.sim_years
        results = solver.solve(baseline_state, sim_years)

        for conv in results:
            assert conv.status == ConvergenceStatus.CONVERGED, (
                f"Year {conv.year} did not converge: "
                f"{conv.iterations} iters, residual={conv.max_residual}"
            )

    def test_solver_iterations_reasonable(self, solver, baseline_state):
        """Solver should converge in reasonable number of iterations."""
        sim_years = baseline_state.sim_years
        results = solver.solve(baseline_state, sim_years)

        for conv in results:
            assert conv.iterations < 500, (
                f"Year {conv.year} took {conv.iterations} iterations"
            )

    def test_solver_residuals_small(self, solver, baseline_state):
        """Max residuals should be very small after convergence."""
        sim_years = baseline_state.sim_years
        results = solver.solve(baseline_state, sim_years)

        for conv in results:
            assert conv.max_residual < 0.001, (
                f"Year {conv.year} residual too large: {conv.max_residual}"
            )
