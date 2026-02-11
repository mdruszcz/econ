"""Accounting identities: GDP, domestic demand, nominal aggregates, ratios."""

import math

from ml2.equations.base import Equation, safe_exp
from ml2.parameters import ML2Scalars
from ml2.state import SimulationState
from ml2.types import EquationType, VarName, Year


class PublicInvestmentEquation(Equation):
    """Public investment: IG = IG[-1] * (1 + g_trend) + VIG_X / 1000."""

    name = "IG_"
    equation_type = EquationType.TECHNICAL
    depends_on = []

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        ig_prev = state.lag("IG_", t)
        trend = ig_prev * (1 + scalars.tfp_growth)  # Grows with trend
        vig_x = state.get("VIG_X", t) if state.has_var("VIG_X") else 0.0
        return trend + vig_x / 1000.0  # mln to bn


class PublicConsumptionEquation(Equation):
    """Public consumption: CG = WG * NG / 1000 + other (trend)."""

    name = "CG_"
    equation_type = EquationType.IDENTITY
    depends_on = ["WG_", "NG_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        wg = state.get("WG_", t)
        ng = state.get("NG_", t)
        # Public consumption = wage bill + non-wage (trending)
        cg_prev = state.lag("CG_", t)
        wg_1 = state.lag("WG_", t)
        ng_1 = state.lag("NG_", t)
        wage_bill = wg * ng / 1000.0  # thousands * k EUR -> bn
        wage_bill_1 = wg_1 * ng_1 / 1000.0
        non_wage = cg_prev - wage_bill_1
        non_wage_trend = non_wage * (1 + scalars.tfp_growth)
        return wage_bill + non_wage_trend


class StockChangeEquation(Equation):
    """Inventory changes: DS = small fraction of GDP, trending."""

    name = "DS_"
    equation_type = EquationType.TECHNICAL
    depends_on = ["Y_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        return state.lag("DS_", t)  # Stock changes ~ stable


class DomesticDemandEquation(Equation):
    """Domestic demand: DD = C + IF + IH + IG + CG + DS."""

    name = "DD_"
    equation_type = EquationType.IDENTITY
    depends_on = ["C_", "IF_", "IH_", "IG_", "CG_", "DS_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        return (
            state.get("C_", t)
            + state.get("IF_", t)
            + state.get("IH_", t)
            + state.get("IG_", t)
            + state.get("CG_", t)
            + state.get("DS_", t)
        )


class GDPEquation(Equation):
    """GDP at constant prices (expenditure side): GDP = DD + X - M."""

    name = "GDP_"
    equation_type = EquationType.IDENTITY
    depends_on = ["DD_", "X_", "M_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        return state.get("DD_", t) + state.get("X_", t) - state.get("M_", t)


class GDPDeflatorEquation(Equation):
    """GDP deflator: weighted average of component deflators."""

    name = "PGDP_"
    equation_type = EquationType.IDENTITY
    depends_on = ["PC_", "PIF_", "PIG_", "PIH_", "PX_", "PM_",
                   "C_", "IF_", "IG_", "IH_", "X_", "M_", "CG_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        gdp = state.get("GDP_", t)
        if gdp == 0:
            return state.lag("PGDP_", t)
        # Nominal GDP / Real GDP
        nom = (
            state.get("C_", t) * state.get("PC_", t)
            + state.get("IF_", t) * state.get("PIF_", t)
            + state.get("IH_", t) * state.get("PIH_", t)
            + state.get("IG_", t) * state.get("PIG_", t)
            + state.get("CG_", t) * state.get("PC_", t)  # Public consumption at CPI
            + state.get("X_", t) * state.get("PX_", t)
            - state.get("M_", t) * state.get("PM_", t)
            + state.get("DS_", t) * state.get("PC_", t)  # Stock changes at CPI
        )
        return nom / gdp


class NominalGDPEquation(Equation):
    """Nominal GDP: GDPN = GDP * PGDP."""

    name = "GDPN_"
    equation_type = EquationType.IDENTITY
    depends_on = ["GDP_", "PGDP_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        return state.get("GDP_", t) * state.get("PGDP_", t)


class TotalInvestmentEquation(Equation):
    """Total investment: I = IF + IH + IG."""

    name = "I_"
    equation_type = EquationType.IDENTITY
    depends_on = ["IF_", "IH_", "IG_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        return state.get("IF_", t) + state.get("IH_", t) + state.get("IG_", t)


class ProfitEquation(Equation):
    """Profit rate: PROFIT = (Y - W*L/1000) / (PC*K)."""

    name = "PROFIT_"
    equation_type = EquationType.IDENTITY
    depends_on = ["Y_", "W_", "L_", "PC_", "K_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        y = state.get("Y_", t)
        w = state.get("W_", t)
        l = state.get("L_", t)
        pc = state.get("PC_", t)
        k = state.get("K_", t)
        if pc * k == 0:
            return state.lag("PROFIT_", t)
        return (y - w * l / 1000.0) / (pc * k)


class RealInterestRateEquation(Equation):
    """Real interest rate: RREAL = R_NOM - inflation."""

    name = "RREAL_"
    equation_type = EquationType.IDENTITY
    depends_on = ["RNOM_", "PC_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        rnom = state.get("RNOM_", t) if state.has_var("RNOM_") else scalars.r_nominal
        # Inflation rate
        pc = state.get("PC_", t)
        pc_1 = state.lag("PC_", t)
        if pc_1 > 0:
            infl = (pc - pc_1) / pc_1
        else:
            infl = 0.0
        return rnom - infl


class MortgageRateEquation(Equation):
    """Mortgage rate: RMORT = RNOM + spread (exogenous)."""

    name = "RMORT_"
    equation_type = EquationType.TECHNICAL
    depends_on = ["RNOM_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        rnom = state.get("RNOM_", t) if state.has_var("RNOM_") else scalars.r_nominal
        return rnom + 0.015  # 1.5pp mortgage spread


class LabourForceEquation(Equation):
    """Labour force: NAT grows at nat_growth rate."""

    name = "NAT_"
    equation_type = EquationType.TECHNICAL
    depends_on = []

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        return state.lag("NAT_", t) * (1 + scalars.nat_growth)


class PublicEmploymentEquation(Equation):
    """Public employment: NG = NG[-1] + NG_X."""

    name = "NG_"
    equation_type = EquationType.TECHNICAL
    depends_on = []

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        ng_prev = state.lag("NG_", t)
        ng_x = state.get("NG_X", t) if state.has_var("NG_X") else 0.0
        return ng_prev + ng_x


class DisposableIncomeEquation(Equation):
    """Household disposable income: YDH = (1 - tax_eff - css_eff) * W * L / 1000 + TGH.

    Simplified: total wages minus taxes/SSC plus transfers.
    """

    name = "YDH_"
    equation_type = EquationType.IDENTITY
    depends_on = ["W_", "L_", "WG_", "NG_", "PC_", "DTH_", "TGH_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        # Private wage bill
        w = state.get("W_", t)
        l = state.get("L_", t)
        private_wages = w * l / 1000.0  # bn EUR

        # Public wage bill
        wg = state.get("WG_", t)
        ng = state.get("NG_", t)
        public_wages = wg * ng / 1000.0

        total_wages = private_wages + public_wages

        # Effective tax rate (accounting for progressivity)
        css_emp = state.get("CSSFR_", t) if state.has_var("CSSFR_") else scalars.css_emp_rate
        css_house = state.get("CSSHR_", t) if state.has_var("CSSHR_") else scalars.css_house_rate

        # Net wages after SSC
        net_wages = total_wages * (1 - css_house)

        # Income tax (as fraction of net wages, ~25% effective rate)
        dth_x = state.get("DTH_X", t) if state.has_var("DTH_X") else 0.0
        base_tax_rate = 0.25
        tax = net_wages * base_tax_rate + dth_x / 1000.0  # Additional tax in bn

        # Transfers
        tgh = state.get("TGH_", t) if state.has_var("TGH_") else 0.0

        return net_wages - tax + tgh


class TransfersEquation(Equation):
    """Government transfers to households: TGH grows with CPI + policy shock."""

    name = "TGH_"
    equation_type = EquationType.TECHNICAL
    depends_on = ["PC_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        tgh_prev = state.lag("TGH_", t)
        dln_pc = state.dln("PC_", t)
        tgh_x = state.get("TGH_X", t) if state.has_var("TGH_X") else 0.0
        return tgh_prev * safe_exp(dln_pc) * (1 + tgh_x / 100.0)


class VATRateEquation(Equation):
    """Effective VAT rate: ITPC0R = ITPC0R_X or baseline."""

    name = "ITPC0R_"
    equation_type = EquationType.TECHNICAL
    depends_on = []

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        if state.has_var("ITPC0R_X"):
            return state.get("ITPC0R_X", t)
        return scalars.vat_rate * 100


class EmployerSSCRateEquation(Equation):
    """Employer SSC rate: CSSFR = CSSFR_X / 100 or baseline."""

    name = "CSSFR_"
    equation_type = EquationType.TECHNICAL
    depends_on = []

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        if state.has_var("CSSFR_X"):
            return state.get("CSSFR_X", t) / 100.0
        return scalars.css_emp_rate


class EmployeeSSCRateEquation(Equation):
    """Employee SSC rate: CSSHR = CSSHR_X / 100 or baseline."""

    name = "CSSHR_"
    equation_type = EquationType.TECHNICAL
    depends_on = []

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        if state.has_var("CSSHR_X"):
            return state.get("CSSHR_X", t) / 100.0
        return scalars.css_house_rate


class NominalInterestRateEquation(Equation):
    """Nominal interest rate: exogenous."""

    name = "RNOM_"
    equation_type = EquationType.TECHNICAL
    depends_on = []

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        return state.lag("RNOM_", t)  # Exogenous, constant


class WorldDemandEquation(Equation):
    """World demand: XWORLD grows at world_growth rate."""

    name = "XWORLD_"
    equation_type = EquationType.TECHNICAL
    depends_on = []

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        return state.lag("XWORLD_", t) * (1 + scalars.world_growth)


class CompetitorPriceEquation(Equation):
    """Foreign competitor price: PCOMP grows at pcomp_growth."""

    name = "PCOMP_"
    equation_type = EquationType.TECHNICAL
    depends_on = []

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        return state.lag("PCOMP_", t) * (1 + scalars.pcomp_growth)


class WageBillEquation(Equation):
    """Total wage bill: WB = W * L / 1000 + WG * NG / 1000."""

    name = "WB_"
    equation_type = EquationType.IDENTITY
    depends_on = ["W_", "L_", "WG_", "NG_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        return (
            state.get("W_", t) * state.get("L_", t) / 1000.0
            + state.get("WG_", t) * state.get("NG_", t) / 1000.0
        )


class ProductivityEquation(Equation):
    """Labour productivity: PROD = Y / LH."""

    name = "PROD_"
    equation_type = EquationType.IDENTITY
    depends_on = ["Y_", "LH_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        lh = state.get("LH_", t)
        if lh == 0:
            return state.lag("PROD_", t)
        return state.get("Y_", t) / lh


IDENTITY_EQUATIONS: list[type[Equation]] = [
    PublicInvestmentEquation,
    PublicConsumptionEquation,
    StockChangeEquation,
    DomesticDemandEquation,
    GDPEquation,
    GDPDeflatorEquation,
    NominalGDPEquation,
    TotalInvestmentEquation,
    ProfitEquation,
    RealInterestRateEquation,
    MortgageRateEquation,
    LabourForceEquation,
    PublicEmploymentEquation,
    DisposableIncomeEquation,
    TransfersEquation,
    VATRateEquation,
    EmployerSSCRateEquation,
    EmployeeSSCRateEquation,
    NominalInterestRateEquation,
    WorldDemandEquation,
    CompetitorPriceEquation,
    WageBillEquation,
    ProductivityEquation,
]
