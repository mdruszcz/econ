"""Production block equations: Y_, K_, TFP_, YSTAR_, YGAP_, ZKF_."""

import math

from ml2.equations.base import Equation
from ml2.parameters import ML2Scalars
from ml2.state import SimulationState
from ml2.types import EquationType, VarName, Year


class TFPEquation(Equation):
    """Total Factor Productivity: TFP_t = TFP_{t-1} * (1 + g_tfp)."""

    name = "TFP_"
    equation_type = EquationType.TECHNICAL
    depends_on = []

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        return state.lag("TFP_", t) * (1 + scalars.tfp_growth)


class CapitalEquation(Equation):
    """Capital accumulation: K_t = IF_t + (1 - delta) * K_{t-1}."""

    name = "K_"
    equation_type = EquationType.IDENTITY
    depends_on = ["IF_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        return state.get("IF_", t) + (1 - scalars.delta) * state.lag("K_", t)


class OutputEquation(Equation):
    """Output (value added): Cobb-Douglas Y = TFP * K^(1-alpha) * LH^alpha."""

    name = "Y_"
    equation_type = EquationType.BEHAVIORAL
    depends_on = ["TFP_", "K_", "LH_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        tfp = state.get("TFP_", t)
        k = state.get("K_", t)
        lh = state.get("LH_", t)
        if k <= 0 or lh <= 0 or tfp <= 0:
            return state.lag("Y_", t)
        return tfp * (k ** (1 - scalars.alpha)) * (lh ** scalars.alpha)


class PotentialOutputEquation(Equation):
    """Potential output: YSTAR uses trend K, TFP, and structural labour."""

    name = "YSTAR_"
    equation_type = EquationType.TECHNICAL
    depends_on = ["TFP_", "K_", "NAT_", "NG_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        tfp = state.get("TFP_", t)
        k = state.get("K_", t)
        # Structural employment = (1 - NAIRU) * NAT - NG
        nat = state.get("NAT_", t)
        ng = state.get("NG_", t)
        l_star = (1 - scalars.nairu) * nat - ng
        # Average hours ~ proportional to LH/L, assume stable ratio
        lh_star = l_star * state.get("LH_", t) / max(state.get("L_", t), 1)
        if k <= 0 or lh_star <= 0:
            return state.lag("YSTAR_", t)
        return tfp * (k ** (1 - scalars.alpha)) * (lh_star ** scalars.alpha)


class OutputGapEquation(Equation):
    """Output gap: YGAP = (Y - YSTAR) / YSTAR."""

    name = "YGAP_"
    equation_type = EquationType.IDENTITY
    depends_on = ["Y_", "YSTAR_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        ystar = state.get("YSTAR_", t)
        if ystar == 0:
            return 0.0
        return (state.get("Y_", t) - ystar) / ystar


class CapacityUtilizationEquation(Equation):
    """Capacity utilization: ZKF = Y / YSTAR, bounded [0.8, 1.1]."""

    name = "ZKF_"
    equation_type = EquationType.IDENTITY
    depends_on = ["Y_", "YSTAR_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        ystar = state.get("YSTAR_", t)
        if ystar == 0:
            return 1.0
        raw = state.get("Y_", t) / ystar
        return max(0.80, min(1.10, raw))


PRODUCTION_EQUATIONS: list[type[Equation]] = [
    TFPEquation,
    CapitalEquation,
    OutputEquation,
    PotentialOutputEquation,
    OutputGapEquation,
    CapacityUtilizationEquation,
]
