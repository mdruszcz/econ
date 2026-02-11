"""Behavioral ECM equations: C_, IF_, IH_, X_, M_ and supporting."""

import math

from ml2.equations.base import Equation, safe_exp as _safe_exp
from ml2.parameters import ML2Scalars
from ml2.state import SimulationState
from ml2.types import EquationType, VarName, Year


class ConsumptionEquation(Equation):
    """Private consumption: ECM with income, interest rate, unemployment.

    dln(C) = c0 + c1*dln(YDH/PC) + c2*d(RREAL) + c3*d(UR)
             + c4*[ln(C) - c5*ln(YDH/PC)][-1] + c6*dln(C)[-1]
    """

    name = "C_"
    equation_type = EquationType.BEHAVIORAL
    depends_on = ["YDH_", "PC_", "UR_", "RREAL_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        c_prev = state.lag("C_", t)
        if c_prev <= 0:
            return c_prev

        # Real disposable income
        ydh = state.get("YDH_", t)
        pc = state.get("PC_", t)
        ydh_1 = state.lag("YDH_", t)
        pc_1 = state.lag("PC_", t)

        if ydh > 0 and pc > 0 and ydh_1 > 0 and pc_1 > 0:
            dln_rydi = math.log(ydh / pc) - math.log(ydh_1 / pc_1)
        else:
            dln_rydi = 0.0

        # Real interest rate change
        rr = state.get("RREAL_", t) if state.has_var("RREAL_") else 0.0
        rr_1 = state.lag("RREAL_", t) if state.has_var("RREAL_") else 0.0
        d_rreal = rr - rr_1

        # Unemployment rate change
        d_ur = state.d("UR_", t)

        # ECM at t-1
        c_1 = state.lag("C_", t)
        if c_1 > 0 and ydh_1 > 0 and pc_1 > 0:
            ecm = math.log(c_1) - scalars.c5 * math.log(ydh_1 / pc_1)
        else:
            ecm = 0.0

        # Lagged consumption growth
        c_2 = state.lag("C_", t, 2) if (t - 2) in state.years else c_1
        if c_2 > 0 and c_1 > 0:
            dln_c_lag = math.log(c_1) - math.log(c_2)
        else:
            dln_c_lag = 0.0

        dln_c = (
            scalars.c0
            + scalars.c1 * dln_rydi
            + scalars.c2 * d_rreal
            + scalars.c3 * d_ur
            + scalars.c4 * ecm
            + scalars.c6 * dln_c_lag
        )
        return c_prev * _safe_exp(dln_c)


class BusinessInvestmentEquation(Equation):
    """Business investment: accelerator + profitability + interest rate + capacity.

    dln(IF) = if0 + if1*dln(Y) + if2*d(PROFIT) + if3*d(RREAL)
              + if4*d(ZKF) + if5*[ln(IF) - if6*ln(Y)][-1]
    """

    name = "IF_"
    equation_type = EquationType.BEHAVIORAL
    depends_on = ["Y_", "PROFIT_", "RREAL_", "ZKF_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        if_prev = state.lag("IF_", t)
        if if_prev <= 0:
            return if_prev

        dln_y = state.dln("Y_", t)

        # Profitability change
        profit = state.get("PROFIT_", t) if state.has_var("PROFIT_") else 0.0
        profit_1 = state.lag("PROFIT_", t) if state.has_var("PROFIT_") else 0.0
        d_profit = profit - profit_1

        # Real interest rate change
        rr = state.get("RREAL_", t) if state.has_var("RREAL_") else 0.0
        rr_1 = state.lag("RREAL_", t) if state.has_var("RREAL_") else 0.0
        d_rreal = rr - rr_1

        # Capacity utilization change
        zkf = state.get("ZKF_", t)
        zkf_1 = state.lag("ZKF_", t)
        d_zkf = zkf - zkf_1

        # ECM at t-1
        y_1 = state.lag("Y_", t)
        if if_prev > 0 and y_1 > 0:
            ecm = math.log(if_prev) - scalars.if6 * math.log(y_1)
        else:
            ecm = 0.0

        dln_if = (
            scalars.if0
            + scalars.if1 * dln_y
            + scalars.if2 * d_profit
            + scalars.if3 * d_rreal
            + scalars.if4 * d_zkf
            + scalars.if5 * ecm
        )
        return if_prev * _safe_exp(dln_if)


class HousingInvestmentEquation(Equation):
    """Housing investment: real income + mortgage rate ECM.

    dln(IH) = ih0 + ih1*dln(YDH/PC) + ih2*d(RMORT)
              + ih3*[ln(IH) - ih4*ln(YDH/PC)][-1]
    """

    name = "IH_"
    equation_type = EquationType.BEHAVIORAL
    depends_on = ["YDH_", "PC_", "RMORT_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        ih_prev = state.lag("IH_", t)
        if ih_prev <= 0:
            return ih_prev

        ydh = state.get("YDH_", t)
        pc = state.get("PC_", t)
        ydh_1 = state.lag("YDH_", t)
        pc_1 = state.lag("PC_", t)

        if ydh > 0 and pc > 0 and ydh_1 > 0 and pc_1 > 0:
            dln_rydi = math.log(ydh / pc) - math.log(ydh_1 / pc_1)
        else:
            dln_rydi = 0.0

        # Mortgage rate change
        rm = state.get("RMORT_", t) if state.has_var("RMORT_") else 0.0
        rm_1 = state.lag("RMORT_", t) if state.has_var("RMORT_") else 0.0
        d_rmort = rm - rm_1

        # ECM at t-1
        if ih_prev > 0 and ydh_1 > 0 and pc_1 > 0:
            ecm = math.log(ih_prev) - scalars.ih4 * math.log(ydh_1 / pc_1)
        else:
            ecm = 0.0

        dln_ih = (
            scalars.ih0
            + scalars.ih1 * dln_rydi
            + scalars.ih2 * d_rmort
            + scalars.ih3 * ecm
        )
        return ih_prev * _safe_exp(dln_ih)


class ExportVolumeEquation(Equation):
    """Export volumes: foreign demand + price competitiveness ECM.

    dln(X) = x0 + x1*dln(XWORLD) + x2*dln(PX/PCOMP)
             + x3*[ln(X) - x4*ln(XWORLD) - x5*ln(PX/PCOMP)][-1]
    """

    name = "X_"
    equation_type = EquationType.BEHAVIORAL
    depends_on = ["XWORLD_", "PX_", "PCOMP_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        x_prev = state.lag("X_", t)
        if x_prev <= 0:
            return x_prev

        # Foreign demand growth
        dln_xw = state.dln("XWORLD_", t) if state.has_var("XWORLD_") else scalars.world_growth

        # Relative price change
        px = state.get("PX_", t)
        pcomp = state.get("PCOMP_", t) if state.has_var("PCOMP_") else 1.0
        px_1 = state.lag("PX_", t)
        pcomp_1 = state.lag("PCOMP_", t) if state.has_var("PCOMP_") else 1.0

        if px > 0 and pcomp > 0 and px_1 > 0 and pcomp_1 > 0:
            dln_relpx = math.log(px / pcomp) - math.log(px_1 / pcomp_1)
        else:
            dln_relpx = 0.0

        # ECM at t-1
        xw_1 = state.lag("XWORLD_", t) if state.has_var("XWORLD_") else 1.0
        if x_prev > 0 and xw_1 > 0 and px_1 > 0 and pcomp_1 > 0:
            ecm = (
                math.log(x_prev)
                - scalars.x4 * math.log(xw_1)
                - scalars.x5 * math.log(px_1 / pcomp_1)
            )
        else:
            ecm = 0.0

        dln_x = scalars.x0 + scalars.x1 * dln_xw + scalars.x2 * dln_relpx + scalars.x3 * ecm
        return x_prev * _safe_exp(dln_x)


class ImportVolumeEquation(Equation):
    """Import volumes: domestic demand + relative price ECM.

    dln(M) = m0 + m1*dln(DD) + m2*dln(PM/PC)
             + m3*[ln(M) - m4*ln(DD) - m5*ln(PM/PC)][-1]
    """

    name = "M_"
    equation_type = EquationType.BEHAVIORAL
    depends_on = ["DD_", "PM_", "PC_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        m_prev = state.lag("M_", t)
        if m_prev <= 0:
            return m_prev

        # Domestic demand growth
        dln_dd = state.dln("DD_", t) if state.has_var("DD_") else 0.0

        # Relative import price change
        pm = state.get("PM_", t) if state.has_var("PM_") else 1.0
        pc = state.get("PC_", t)
        pm_1 = state.lag("PM_", t) if state.has_var("PM_") else 1.0
        pc_1 = state.lag("PC_", t)

        if pm > 0 and pc > 0 and pm_1 > 0 and pc_1 > 0:
            dln_relpm = math.log(pm / pc) - math.log(pm_1 / pc_1)
        else:
            dln_relpm = 0.0

        # ECM at t-1
        dd_1 = state.lag("DD_", t) if state.has_var("DD_") else 1.0
        if m_prev > 0 and dd_1 > 0 and pm_1 > 0 and pc_1 > 0:
            ecm = (
                math.log(m_prev)
                - scalars.m4 * math.log(dd_1)
                - scalars.m5 * math.log(pm_1 / pc_1)
            )
        else:
            ecm = 0.0

        dln_m = scalars.m0 + scalars.m1 * dln_dd + scalars.m2 * dln_relpm + scalars.m3 * ecm
        return m_prev * _safe_exp(dln_m)


BEHAVIORAL_EQUATIONS: list[type[Equation]] = [
    ConsumptionEquation,
    BusinessInvestmentEquation,
    HousingInvestmentEquation,
    ExportVolumeEquation,
    ImportVolumeEquation,
]
