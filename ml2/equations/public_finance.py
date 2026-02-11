"""Public finance equations: government receipts, expenditures, deficit, debt."""

from ml2.equations.base import Equation
from ml2.parameters import ML2Scalars
from ml2.state import SimulationState
from ml2.types import EquationType, VarName, Year


class GovernmentReceiptsEquation(Equation):
    """Total government receipts:
    GRECEIPTS = income_tax + VAT_revenue + SSC_employer + SSC_employee + other.
    """

    name = "GRECEIPTS_"
    equation_type = EquationType.IDENTITY
    depends_on = ["W_", "L_", "WG_", "NG_", "C_", "PC_", "ITPC0R_",
                   "CSSFR_", "CSSHR_", "GDPN_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        # Wage bill (bn EUR)
        private_wb = state.get("W_", t) * state.get("L_", t) / 1000.0
        public_wb = state.get("WG_", t) * state.get("NG_", t) / 1000.0
        total_wb = private_wb + public_wb

        # Employer SSC
        cssfr = state.get("CSSFR_", t) if state.has_var("CSSFR_") else scalars.css_emp_rate
        ssc_emp = total_wb * cssfr

        # Employee SSC
        csshr = state.get("CSSHR_", t) if state.has_var("CSSHR_") else scalars.css_house_rate
        ssc_house = total_wb * csshr

        # Income tax (progressive, ~25% effective rate on net wages)
        dth_x = state.get("DTH_X", t) if state.has_var("DTH_X") else 0.0
        income_tax = total_wb * (1 - csshr) * 0.25 + dth_x / 1000.0

        # VAT revenue
        vat_rate = state.get("ITPC0R_", t) if state.has_var("ITPC0R_") else scalars.vat_rate * 100
        consumption_nom = state.get("C_", t) * state.get("PC_", t)
        vat_revenue = consumption_nom * (vat_rate / 100.0) / (1 + vat_rate / 100.0)

        # Other revenue (~12% of nominal GDP)
        gdpn = state.get("GDPN_", t)
        other_revenue = gdpn * 0.12

        return income_tax + vat_revenue + ssc_emp + ssc_house + other_revenue


class GovernmentExpenditureEquation(Equation):
    """Total government expenditure:
    GEXPENSE = CG*PC + IG*PIG + transfers + interest payments.
    """

    name = "GEXPENSE_"
    equation_type = EquationType.IDENTITY
    depends_on = ["CG_", "PC_", "IG_", "PIG_", "TGH_", "B_", "GDPN_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        # Public consumption (nominal)
        cg_nom = state.get("CG_", t) * state.get("PC_", t)

        # Public investment (nominal)
        ig_nom = state.get("IG_", t) * state.get("PIG_", t)

        # Transfers to households
        tgh = state.get("TGH_", t)

        # Interest payments on debt
        b = state.get("B_", t) if state.has_var("B_") else (
            state.get("GDPN_", t) * scalars.debt_gdp
        )
        interest = b * scalars.debt_rate

        # Other expenditure (~8% of nominal GDP)
        gdpn = state.get("GDPN_", t)
        other_exp = gdpn * 0.08

        return cg_nom + ig_nom + tgh + interest + other_exp


class DeficitEquation(Equation):
    """Government deficit (surplus if positive): D = GRECEIPTS - GEXPENSE."""

    name = "D_"
    equation_type = EquationType.IDENTITY
    depends_on = ["GRECEIPTS_", "GEXPENSE_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        return state.get("GRECEIPTS_", t) - state.get("GEXPENSE_", t)


class DebtEquation(Equation):
    """Public debt accumulation: B = B[-1] - D (deficit adds to debt)."""

    name = "B_"
    equation_type = EquationType.IDENTITY
    depends_on = ["D_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        return state.lag("B_", t) - state.get("D_", t)


class DeficitRatioEquation(Equation):
    """Deficit as % of GDP: DR = D / GDPN (negative = deficit)."""

    name = "DR_"
    equation_type = EquationType.IDENTITY
    depends_on = ["D_", "GDPN_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        gdpn = state.get("GDPN_", t)
        if gdpn == 0:
            return 0.0
        return state.get("D_", t) / gdpn


class DebtRatioEquation(Equation):
    """Debt as % of GDP: BR = B / GDPN."""

    name = "BR_"
    equation_type = EquationType.IDENTITY
    depends_on = ["B_", "GDPN_"]

    def compute(self, state: SimulationState, t: Year, scalars: ML2Scalars) -> float:
        gdpn = state.get("GDPN_", t)
        if gdpn == 0:
            return state.lag("BR_", t)
        return state.get("B_", t) / gdpn


PUBLIC_FINANCE_EQUATIONS: list[type[Equation]] = [
    GovernmentReceiptsEquation,
    GovernmentExpenditureEquation,
    DeficitEquation,
    DebtEquation,
    DeficitRatioEquation,
    DebtRatioEquation,
]
