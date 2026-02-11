"""Labour market equations: LH_, L_, U_, UR_, W_."""

import math

from ml2.equations.base import Equation, safe_exp
from ml2.parameters import ML2Scalars
from ml2.state import SimulationState
from ml2.types import EquationType, VarName, Year


class LabourHoursEquation(Equation):
    """Labour demand (hours): ECM on output and productivity.

    dln(LH) = lh0 + lh1*dln(Y) + lh2*[ln(Y) - (1-alpha)*ln(K[-1]) - ln(TFP) - alpha*ln(LH)][-1]
    """

    name = "LH_"
    equation_type = EquationType.BEHAVIORAL
    depends_on = ["Y_", "K_", "TFP_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        lh_prev = state.lag("LH_", t)
        if lh_prev <= 0:
            return lh_prev

        dln_y = state.dln("Y_", t)

        # ECM term at t-1
        y_1 = state.lag("Y_", t)
        k_1 = state.lag("K_", t)
        tfp_1 = state.lag("TFP_", t)
        lh_1 = lh_prev
        if y_1 > 0 and k_1 > 0 and tfp_1 > 0 and lh_1 > 0:
            ecm = (
                math.log(y_1)
                - (1 - scalars.alpha) * math.log(k_1)
                - math.log(tfp_1)
                - scalars.alpha * math.log(lh_1)
            )
        else:
            ecm = 0.0

        dln_lh = scalars.lh0 + scalars.lh1 * dln_y + scalars.lh2 * ecm
        return lh_prev * safe_exp(dln_lh)


class EmploymentEquation(Equation):
    """Employment (persons): L = LH / average_hours.

    Average hours treated as slowly trending exogenous.
    L tracks LH growth.
    """

    name = "L_"
    equation_type = EquationType.IDENTITY
    depends_on = ["LH_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        lh = state.get("LH_", t)
        lh_prev = state.lag("LH_", t)
        l_prev = state.lag("L_", t)
        if lh_prev == 0 or l_prev == 0:
            return l_prev
        # Hours per worker ratio stays ~ constant
        return l_prev * (lh / lh_prev)


class UnemploymentEquation(Equation):
    """Unemployment: U = NAT - L - NG."""

    name = "U_"
    equation_type = EquationType.IDENTITY
    depends_on = ["NAT_", "L_", "NG_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        return state.get("NAT_", t) - state.get("L_", t) - state.get("NG_", t)


class UnemploymentRateEquation(Equation):
    """Unemployment rate: UR = U / NAT."""

    name = "UR_"
    equation_type = EquationType.IDENTITY
    depends_on = ["U_", "NAT_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        nat = state.get("NAT_", t)
        if nat == 0:
            return 0.0
        return state.get("U_", t) / nat


class WageEquation(Equation):
    """Private sector wages: Phillips curve + indexation + productivity ECM.

    dln(W) = w0 + w1*dln(PC) + w2*dln(PROD) + w3*(UR - NAIRU) + w4*(WS[-1] - w5)
    where PROD = Y/LH, WS = W*L / (PC*Y)
    """

    name = "W_"
    equation_type = EquationType.BEHAVIORAL
    depends_on = ["PC_", "Y_", "LH_", "L_", "UR_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        w_prev = state.lag("W_", t)
        if w_prev <= 0:
            return w_prev

        dln_pc = state.dln("PC_", t)

        # Productivity growth
        y = state.get("Y_", t)
        lh = state.get("LH_", t)
        y_1 = state.lag("Y_", t)
        lh_1 = state.lag("LH_", t)
        if y > 0 and lh > 0 and y_1 > 0 and lh_1 > 0:
            dln_prod = math.log(y / lh) - math.log(y_1 / lh_1)
        else:
            dln_prod = 0.0

        # Phillips curve: unemployment gap
        ur = state.get("UR_", t)
        ur_gap = ur - scalars.nairu

        # Wage share convergence (ECM)
        l_1 = state.lag("L_", t)
        pc_1 = state.lag("PC_", t)
        if y_1 > 0 and pc_1 > 0:
            ws_1 = (w_prev * l_1) / (pc_1 * y_1 * 1000)  # Adjust units
        else:
            ws_1 = scalars.w5

        dln_w = (
            scalars.w0
            + scalars.w1 * dln_pc
            + scalars.w2 * dln_prod
            + scalars.w3 * ur_gap
            + scalars.w4 * (ws_1 - scalars.w5)
        )

        # Apply wage correction instrument if present
        wr_x = state.get("WR_X", t) if state.has_var("WR_X") else 0.0
        dln_w += wr_x / 100.0

        # Apply indexation correction
        zx_x = state.get("ZX_X", t) if state.has_var("ZX_X") else 0.0
        dln_w += zx_x / 100.0

        return w_prev * safe_exp(dln_w)


class PublicWageEquation(Equation):
    """Public sector wages: indexed to CPI + exogenous real growth.

    WG = WG[-1] * (1 + dln(PC) + WGRR_X/100)
    """

    name = "WG_"
    equation_type = EquationType.TECHNICAL
    depends_on = ["PC_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        wg_prev = state.lag("WG_", t)
        dln_pc = state.dln("PC_", t)
        wgrr = state.get("WGRR_X", t) if state.has_var("WGRR_X") else 0.0
        return wg_prev * safe_exp(dln_pc + wgrr / 100.0)


LABOR_EQUATIONS: list[type[Equation]] = [
    LabourHoursEquation,
    EmploymentEquation,
    UnemploymentEquation,
    UnemploymentRateEquation,
    WageEquation,
    PublicWageEquation,
]
