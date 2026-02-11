"""Price equations: PC_, PIF_, PIG_, PIH_, PX_, COST_, PM_, ULC_."""

import math

from ml2.equations.base import Equation, safe_exp
from ml2.parameters import ML2Scalars
from ml2.state import SimulationState
from ml2.types import EquationType, VarName, Year


class UnitLabourCostEquation(Equation):
    """Unit labour cost: ULC = W * L / Y."""

    name = "ULC_"
    equation_type = EquationType.IDENTITY
    depends_on = ["W_", "L_", "Y_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        y = state.get("Y_", t)
        if y == 0:
            return state.lag("ULC_", t)
        return state.get("W_", t) * state.get("L_", t) / y


class MacroCostEquation(Equation):
    """Macro cost index: COST = cost_w * ULC + cost_pm * PM."""

    name = "COST_"
    equation_type = EquationType.IDENTITY
    depends_on = ["ULC_", "PM_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        ulc = state.get("ULC_", t)
        pm = state.get("PM_", t) if state.has_var("PM_") else state.lag("PM_", t)
        return scalars.cost_w * ulc + scalars.cost_pm * pm


class ConsumerPriceEquation(Equation):
    """Consumer prices (CPI): cost push + VAT + output gap ECM.

    dln(PC) = pc0 + pc1*dln(COST) + pc2*dln(PM) + pc3*YGAP
              + pc4*[ln(PC) - pc5*ln(COST)][-1] + pc_vat*d(ITPC0R/100)
    """

    name = "PC_"
    equation_type = EquationType.BEHAVIORAL
    depends_on = ["COST_", "PM_", "YGAP_", "ITPC0R_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        pc_prev = state.lag("PC_", t)
        if pc_prev <= 0:
            return pc_prev

        # Cost push
        dln_cost = state.dln("COST_", t)

        # Import price pass-through
        dln_pm = state.dln("PM_", t) if state.has_var("PM_") else scalars.pm_growth

        # Output gap
        ygap = state.get("YGAP_", t)

        # ECM at t-1
        cost_1 = state.lag("COST_", t)
        if pc_prev > 0 and cost_1 > 0:
            ecm = math.log(pc_prev) - scalars.pc5 * math.log(cost_1)
        else:
            ecm = 0.0

        # VAT effect
        vat = state.get("ITPC0R_", t) if state.has_var("ITPC0R_") else scalars.vat_rate * 100
        vat_1 = state.lag("ITPC0R_", t) if state.has_var("ITPC0R_") else scalars.vat_rate * 100
        d_vat = (vat - vat_1) / 100.0  # Convert from pp to fraction

        dln_pc = (
            scalars.pc0
            + scalars.pc1 * dln_cost
            + scalars.pc2 * dln_pm
            + scalars.pc3 * ygap
            + scalars.pc4 * ecm
            + scalars.pc_vat * d_vat
        )
        return pc_prev * safe_exp(dln_pc)


class BusinessInvestmentDeflatorEquation(Equation):
    """Business investment deflator: cost push + import price ECM.

    dln(PIF) = pif1*dln(COST) + pif2*dln(PM) + pif3*[ln(PIF) - ln(COST)][-1]
    """

    name = "PIF_"
    equation_type = EquationType.BEHAVIORAL
    depends_on = ["COST_", "PM_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        pif_prev = state.lag("PIF_", t)
        if pif_prev <= 0:
            return pif_prev

        dln_cost = state.dln("COST_", t)
        dln_pm = state.dln("PM_", t) if state.has_var("PM_") else scalars.pm_growth

        cost_1 = state.lag("COST_", t)
        if pif_prev > 0 and cost_1 > 0:
            ecm = math.log(pif_prev) - math.log(cost_1)
        else:
            ecm = 0.0

        dln_pif = scalars.pif1 * dln_cost + scalars.pif2 * dln_pm + scalars.pif3 * ecm
        return pif_prev * safe_exp(dln_pif)


class HousingInvestmentDeflatorEquation(Equation):
    """Housing investment deflator: construction cost ECM.

    dln(PIH) = pih1*dln(COST) + pih2*dln(PM) + pih3*[ln(PIH) - ln(COST)][-1]
    """

    name = "PIH_"
    equation_type = EquationType.BEHAVIORAL
    depends_on = ["COST_", "PM_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        pih_prev = state.lag("PIH_", t)
        if pih_prev <= 0:
            return pih_prev

        dln_cost = state.dln("COST_", t)
        dln_pm = state.dln("PM_", t) if state.has_var("PM_") else scalars.pm_growth

        cost_1 = state.lag("COST_", t)
        if pih_prev > 0 and cost_1 > 0:
            ecm = math.log(pih_prev) - math.log(cost_1)
        else:
            ecm = 0.0

        dln_pih = scalars.pih1 * dln_cost + scalars.pih2 * dln_pm + scalars.pih3 * ecm
        return pih_prev * safe_exp(dln_pih)


class PublicInvestmentDeflatorEquation(Equation):
    """Public investment deflator: follows cost index.

    dln(PIG) = pig1*dln(COST) + pig2*dln(PM)
    """

    name = "PIG_"
    equation_type = EquationType.TECHNICAL
    depends_on = ["COST_", "PM_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        pig_prev = state.lag("PIG_", t)
        if pig_prev <= 0:
            return pig_prev
        dln_cost = state.dln("COST_", t)
        dln_pm = state.dln("PM_", t) if state.has_var("PM_") else scalars.pm_growth
        dln_pig = scalars.pig1 * dln_cost + scalars.pig2 * dln_pm
        return pig_prev * safe_exp(dln_pig)


class ExportPriceEquation(Equation):
    """Export price: domestic cost vs foreign competitor price ECM.

    dln(PX) = px1*dln(COST) + px2*dln(PCOMP) + px3*[ln(PX) - ln(PCOMP)][-1]
    """

    name = "PX_"
    equation_type = EquationType.BEHAVIORAL
    depends_on = ["COST_", "PCOMP_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        px_prev = state.lag("PX_", t)
        if px_prev <= 0:
            return px_prev

        dln_cost = state.dln("COST_", t)
        dln_pcomp = (
            state.dln("PCOMP_", t) if state.has_var("PCOMP_") else scalars.pcomp_growth
        )

        pcomp_1 = state.lag("PCOMP_", t) if state.has_var("PCOMP_") else 1.0
        if px_prev > 0 and pcomp_1 > 0:
            ecm = math.log(px_prev) - math.log(pcomp_1)
        else:
            ecm = 0.0

        dln_px = scalars.px1 * dln_cost + scalars.px2 * dln_pcomp + scalars.px3 * ecm
        return px_prev * safe_exp(dln_px)


class ImportPriceEquation(Equation):
    """Import price: exogenous trend growing at pm_growth.

    PM grows at world import price growth rate.
    """

    name = "PM_"
    equation_type = EquationType.TECHNICAL
    depends_on = []

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        pm_prev = state.lag("PM_", t)
        return pm_prev * (1 + scalars.pm_growth)


PRICE_EQUATIONS: list[type[Equation]] = [
    UnitLabourCostEquation,
    MacroCostEquation,
    ConsumerPriceEquation,
    BusinessInvestmentDeflatorEquation,
    HousingInvestmentDeflatorEquation,
    PublicInvestmentDeflatorEquation,
    ExportPriceEquation,
    ImportPriceEquation,
]
