"""Impact calculation: (Scenario - Baseline) / Baseline x 100."""

from __future__ import annotations

from ml2.state import SimulationState
from ml2.types import VarName, Year

# Variables where impact is absolute difference (ratio variables)
ABSOLUTE_IMPACT_VARS: set[VarName] = {"DR_", "UR_", "BR_", "TBR_", "YGAP_", "ZKF_"}


def compute_impacts(
    baseline: SimulationState,
    scenario: SimulationState,
    variables: list[VarName],
    sim_years: list[Year],
) -> dict[VarName, dict[Year, float]]:
    """Compute percentage or absolute impacts for each variable/year.

    For level variables: ((scenario - baseline) / baseline) * 100
    For ratio variables (DR_, UR_, etc.): (scenario - baseline) * 100  (pp)
    """
    impacts: dict[VarName, dict[Year, float]] = {}

    for var in variables:
        impacts[var] = {}
        for t in sim_years:
            base_val = baseline.get(var, t)
            scen_val = scenario.get(var, t)

            if var in ABSOLUTE_IMPACT_VARS:
                # Absolute difference in percentage points
                impacts[var][t] = (scen_val - base_val) * 100
            else:
                # Percentage deviation
                if abs(base_val) > 1e-10:
                    impacts[var][t] = (scen_val - base_val) / base_val * 100
                else:
                    impacts[var][t] = 0.0

    return impacts
