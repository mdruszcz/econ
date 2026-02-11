"""SimulationEngine: orchestrates baseline loading, instrument application, solving."""

from __future__ import annotations

from dataclasses import dataclass, field

from ml2.equations.registry import EquationRegistry
from ml2.impact import compute_impacts
from ml2.instruments import (
    INSTRUMENTS,
    apply_instruments,
    get_default_instruments,
    validate_instruments,
)
from ml2.parameters import ML2Scalars
from ml2.solver import GaussSeidelSolver, YearConvergence
from ml2.state import SimulationState
from ml2.types import VarName, Year
from ml2.variables import KEY_INDICATORS, BaselineDataLoader


@dataclass
class KeyIndicators:
    """Key macro indicators for dashboard display."""

    years: list[Year]
    gdp_growth: list[float]       # grt(GDP_) %
    inflation: list[float]        # grt(PC_) %
    deficit_ratio: list[float]    # DR_ * 100 %
    unemployment: list[float]     # UR_ * 100 %


@dataclass
class SimulationOutput:
    """Complete simulation results."""

    name: str
    years: list[Year]
    baseline_indicators: KeyIndicators
    scenario_indicators: KeyIndicators
    impacts: dict[VarName, dict[Year, float]]
    levels: dict[VarName, dict[Year, float]]
    convergence: list[dict]
    instruments: dict[str, float]


class SimulationEngine:
    """Main orchestrator: loads baseline, applies instruments, solves, computes impacts."""

    def __init__(self) -> None:
        self._loader = BaselineDataLoader()
        self._scalars = ML2Scalars()
        self._registry = EquationRegistry()
        self._solver = GaussSeidelSolver(self._registry, self._scalars)
        self._baseline: SimulationState | None = None

    def load_baseline(self) -> None:
        """Load baseline data from disk and ensure all model variables exist."""
        self._baseline = self._loader.load_state()
        self._ensure_variables(self._baseline)

    def _ensure_variables(self, state: SimulationState) -> None:
        """Add any missing variables that the solver needs, with sensible defaults."""
        s = self._scalars
        years = state.years

        # Helper to add variable if missing and set values
        def ensure(var: str, fn) -> None:
            if not state.has_var(var):
                state.add_var(var)
            for yr in years:
                if state.get(var, yr) == 0.0:
                    state.set(var, yr, fn(yr))

        # Y_ (value added) ~ GDP
        ensure("Y_", lambda yr: state.get("GDP_", yr))

        # DD_ (domestic demand)
        ensure("DD_", lambda yr: (
            state.get("C_", yr) + state.get("IF_", yr) + state.get("IH_", yr)
            + state.get("IG_", yr) + state.get("CG_", yr) + state.get("DS_", yr)
        ))

        # RREAL_ (real interest rate)
        ensure("RREAL_", lambda yr: s.r_nominal - 0.015)

        # RMORT_ (mortgage rate)
        ensure("RMORT_", lambda yr: state.get("RNOM_", yr) + 0.015 if state.has_var("RNOM_") else 0.045)

        # PROFIT_ (profit rate)
        def profit_fn(yr):
            y = state.get("GDP_", yr)
            w = state.get("W_", yr)
            l = state.get("L_", yr)
            pc = state.get("PC_", yr)
            k = state.get("K_", yr)
            if pc * k > 0:
                return (y - w * l / 1000.0) / (pc * k)
            return 0.06
        ensure("PROFIT_", profit_fn)

        # ULC_ (unit labour cost)
        def ulc_fn(yr):
            y = state.get("GDP_", yr)
            if y > 0:
                return state.get("W_", yr) * state.get("L_", yr) / y
            return 0.0
        ensure("ULC_", ulc_fn)

        # COST_ (macro cost)
        def cost_fn(yr):
            ulc = state.get("ULC_", yr)
            pm = state.get("PM_", yr) if state.has_var("PM_") else 1.0
            return s.cost_w * ulc + s.cost_pm * pm
        ensure("COST_", cost_fn)

        # Ensure all remaining registry variables exist
        for var in self._registry.all_variables:
            if not state.has_var(var):
                state.add_var(var, 0.0)

    @property
    def baseline(self) -> SimulationState:
        if self._baseline is None:
            self.load_baseline()
        return self._baseline  # type: ignore[return-value]

    def _extract_indicators(self, state: SimulationState, sim_years: list[Year]) -> KeyIndicators:
        """Extract key indicators from a simulation state."""
        return KeyIndicators(
            years=sim_years,
            gdp_growth=[state.grt("GDP_", t) for t in sim_years],
            inflation=[state.grt("PC_", t) for t in sim_years],
            deficit_ratio=[state.get("DR_", t) * 100 for t in sim_years],
            unemployment=[state.get("UR_", t) * 100 for t in sim_years],
        )

    def simulate(
        self,
        instrument_values: dict[str, float] | None = None,
        name: str = "Scenario",
    ) -> SimulationOutput:
        """Run a simulation with given instrument values.

        Args:
            instrument_values: Dict of instrument_key -> value. Missing keys use defaults.
            name: Scenario name for labeling.

        Returns:
            SimulationOutput with baseline/scenario indicators, impacts, levels, convergence.
        """
        # Merge with defaults
        instruments = get_default_instruments()
        if instrument_values:
            errors = validate_instruments(instrument_values)
            if errors:
                raise ValueError(f"Invalid instruments: {'; '.join(errors)}")
            instruments.update(instrument_values)

        # Copy baseline state for scenario
        baseline_state = self.baseline.copy()
        scenario_state = self.baseline.copy()
        sim_years = scenario_state.sim_years

        # Apply instruments to scenario
        apply_instruments(scenario_state, instruments, sim_years)

        # Solve scenario
        convergence = self._solver.solve(scenario_state, sim_years)

        # Extract indicators
        baseline_ind = self._extract_indicators(baseline_state, sim_years)
        scenario_ind = self._extract_indicators(scenario_state, sim_years)

        # Compute impacts for all tracked variables
        all_vars = self._registry.all_variables
        impacts = compute_impacts(baseline_state, scenario_state, all_vars, sim_years)

        # Extract levels for key variables
        level_vars = [
            "GDP_", "C_", "IF_", "IH_", "IG_", "X_", "M_",
            "PC_", "W_", "L_", "U_", "UR_", "DR_", "BR_",
            "YDH_", "GDPN_", "K_", "PROD_", "ULC_",
            "GRECEIPTS_", "GEXPENSE_", "D_", "B_",
        ]
        levels = scenario_state.to_dict(level_vars)

        return SimulationOutput(
            name=name,
            years=sim_years,
            baseline_indicators=baseline_ind,
            scenario_indicators=scenario_ind,
            impacts=impacts,
            levels=levels,
            convergence=[
                {
                    "year": c.year,
                    "iterations": c.iterations,
                    "max_residual": round(c.max_residual, 8),
                    "status": c.status.name,
                }
                for c in convergence
            ],
            instruments=instruments,
        )

    def get_baseline_indicators(self) -> KeyIndicators:
        """Return baseline key indicators without running a simulation."""
        state = self.baseline
        sim_years = state.sim_years
        return self._extract_indicators(state, sim_years)

    def get_instrument_specs(self) -> list[dict]:
        """Return instrument specifications."""
        return [
            {
                "key": i.key,
                "label": i.label,
                "unit": i.unit,
                "default": i.default,
                "min": i.min_val,
                "max": i.max_val,
                "description": i.description,
            }
            for i in INSTRUMENTS
        ]
