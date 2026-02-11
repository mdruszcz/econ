"""Foreign trade equations: nominal exports/imports, trade balance."""

from ml2.equations.base import Equation
from ml2.parameters import ML2Scalars
from ml2.state import SimulationState
from ml2.types import EquationType, VarName, Year


class NominalExportsEquation(Equation):
    """Nominal exports: XN = X * PX."""

    name = "XN_"
    equation_type = EquationType.IDENTITY
    depends_on = ["X_", "PX_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        return state.get("X_", t) * state.get("PX_", t)


class NominalImportsEquation(Equation):
    """Nominal imports: MN = M * PM."""

    name = "MN_"
    equation_type = EquationType.IDENTITY
    depends_on = ["M_", "PM_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        return state.get("M_", t) * state.get("PM_", t)


class TradeBalanceEquation(Equation):
    """Trade balance: TB = XN - MN."""

    name = "TB_"
    equation_type = EquationType.IDENTITY
    depends_on = ["XN_", "MN_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        return state.get("XN_", t) - state.get("MN_", t)


class TradeBalanceRatioEquation(Equation):
    """Trade balance as % of GDP: TBR = TB / GDPN."""

    name = "TBR_"
    equation_type = EquationType.IDENTITY
    depends_on = ["TB_", "GDPN_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        gdpn = state.get("GDPN_", t)
        if gdpn == 0:
            return 0.0
        return state.get("TB_", t) / gdpn


FOREIGN_EQUATIONS: list[type[Equation]] = [
    NominalExportsEquation,
    NominalImportsEquation,
    TradeBalanceEquation,
    TradeBalanceRatioEquation,
]
