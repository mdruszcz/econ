"""Equation registry: maps variable names to equations with 3-phase solve order."""

from ml2.equations.base import Equation
from ml2.equations.behavioral import BEHAVIORAL_EQUATIONS
from ml2.equations.foreign import FOREIGN_EQUATIONS
from ml2.equations.identities import IDENTITY_EQUATIONS
from ml2.equations.labor import LABOR_EQUATIONS
from ml2.equations.prices import PRICE_EQUATIONS
from ml2.equations.production import PRODUCTION_EQUATIONS
from ml2.equations.public_finance import PUBLIC_FINANCE_EQUATIONS
from ml2.types import VarName


class EquationRegistry:
    """Central registry mapping VarName -> Equation instance.

    Classifies equations into three phases for Gauss-Seidel solving:
    - PRE: exogenous links, instrument mappings, technical trends
    - INTER: interdependent behavioral + identity equations (iterative)
    - POST: derived ratios and diagnostics
    """

    def __init__(self) -> None:
        self._equations: dict[VarName, Equation] = {}
        self._pre_order: list[VarName] = []
        self._inter_order: list[VarName] = []
        self._post_order: list[VarName] = []
        self._build()

    def _build(self) -> None:
        """Register all equations and classify into solve phases."""
        all_eq_classes = (
            PRODUCTION_EQUATIONS
            + LABOR_EQUATIONS
            + BEHAVIORAL_EQUATIONS
            + PRICE_EQUATIONS
            + IDENTITY_EQUATIONS
            + PUBLIC_FINANCE_EQUATIONS
            + FOREIGN_EQUATIONS
        )

        for cls in all_eq_classes:
            eq = cls()
            self._equations[eq.name] = eq

        # Phase 1 (PRE-recursive): exogenous trends, instrument mappings
        self._pre_order = [
            "TFP_",       # TFP trend
            "NAT_",       # Labour force trend
            "NG_",        # Public employment
            "XWORLD_",    # World demand
            "PCOMP_",     # Competitor prices
            "PM_",        # Import prices
            "RNOM_",      # Nominal interest rate
            "RMORT_",     # Mortgage rate
            "ITPC0R_",    # VAT rate
            "CSSFR_",     # Employer SSC rate
            "CSSHR_",     # Employee SSC rate
            "IG_",        # Public investment
            "TGH_",       # Transfers
            "DS_",        # Stock changes
        ]

        # Phase 2 (INTER-dependent): iterative Gauss-Seidel block
        # Order designed to minimize iterations (output -> labor -> wages ->
        # prices -> income -> demand -> trade -> GDP -> back to output)
        self._inter_order = [
            "K_",         # Capital stock
            "Y_",         # Output (Cobb-Douglas)
            "YSTAR_",     # Potential output
            "YGAP_",      # Output gap
            "ZKF_",       # Capacity utilization
            "LH_",        # Labour hours
            "L_",         # Employment
            "U_",         # Unemployment
            "UR_",        # Unemployment rate
            "W_",         # Private wages
            "WG_",        # Public wages
            "ULC_",       # Unit labour cost
            "COST_",      # Macro cost index
            "PC_",        # Consumer prices
            "PIF_",       # Business investment deflator
            "PIH_",       # Housing investment deflator
            "PIG_",       # Public investment deflator
            "PX_",        # Export prices
            "RREAL_",     # Real interest rate
            "PROFIT_",    # Profit rate
            "CG_",        # Public consumption
            "YDH_",       # Disposable income
            "C_",         # Private consumption
            "IF_",        # Business investment
            "IH_",        # Housing investment
            "DD_",        # Domestic demand
            "X_",         # Exports
            "M_",         # Imports
            "GDP_",       # GDP
            "PGDP_",      # GDP deflator
            "GDPN_",      # Nominal GDP
            "GRECEIPTS_", # Government receipts
            "GEXPENSE_",  # Government expenditure
            "D_",         # Deficit
            "B_",         # Debt
        ]

        # Phase 3 (POST-recursive): derived ratios
        self._post_order = [
            "I_",         # Total investment
            "PROD_",      # Productivity
            "WB_",        # Wage bill
            "DR_",        # Deficit ratio
            "BR_",        # Debt ratio
            "XN_",        # Nominal exports
            "MN_",        # Nominal imports
            "TB_",        # Trade balance
            "TBR_",       # Trade balance ratio
        ]

    def get(self, var: VarName) -> Equation | None:
        return self._equations.get(var)

    @property
    def pre_order(self) -> list[VarName]:
        return self._pre_order

    @property
    def inter_order(self) -> list[VarName]:
        return self._inter_order

    @property
    def post_order(self) -> list[VarName]:
        return self._post_order

    @property
    def all_variables(self) -> list[VarName]:
        return self._pre_order + self._inter_order + self._post_order

    def __len__(self) -> int:
        return len(self._equations)
