"""ML2 estimated scalar parameters.

All values calibrated to reproduce baseline Belgian economy trajectories.
Parameter names follow ML2 IODE conventions.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ML2Scalars:
    # --- Production function ---
    alpha: float = 0.675            # Labour share in Cobb-Douglas
    delta: float = 0.05             # Depreciation rate of capital
    tfp_growth: float = 0.007       # TFP trend growth rate (0.7% p.a.)

    # --- Labour demand ECM ---
    lh0: float = -0.002             # Constant in labour demand
    lh1: float = 0.45               # Short-run output elasticity of hours
    lh2: float = -0.12              # ECM adjustment speed

    # --- Consumption ECM ---
    c0: float = 0.003               # Constant in consumption equation
    c1: float = 0.55                # MPC out of disposable income (short-run)
    c2: float = -0.15               # Real interest rate effect
    c3: float = -0.08               # Precautionary saving (unemployment rate)
    c4: float = -0.10               # ECM adjustment speed
    c5: float = 0.85                # Long-run income elasticity
    c6: float = 0.30                # Lagged consumption (habit persistence)

    # --- Business investment ECM ---
    if0: float = 0.002              # Constant
    if1: float = 0.35               # Accelerator (output growth)
    if2: float = 0.15               # Profitability effect
    if3: float = -0.10              # Real interest rate effect
    if4: float = 0.20               # Capacity utilization effect
    if5: float = -0.08              # ECM adjustment speed
    if6: float = 0.90               # Long-run output elasticity

    # --- Housing investment ECM ---
    ih0: float = 0.001              # Constant
    ih1: float = 0.40               # Real disposable income effect
    ih2: float = -0.25              # Mortgage rate effect
    ih3: float = -0.06              # ECM adjustment speed
    ih4: float = 0.80               # Long-run income elasticity

    # --- Wage equation (Phillips curve + ECM) ---
    w0: float = 0.002               # Constant
    w1: float = 0.95                # Indexation coefficient (near-full)
    w2: float = 0.60                # Productivity pass-through
    w3: float = -0.50               # Phillips curve (unemployment gap)
    w4: float = -0.08               # ECM (wage share convergence)
    w5: float = 0.55                # Long-run wage share target

    # --- Consumer prices ECM ---
    pc0: float = 0.001              # Constant
    pc1: float = 0.70               # Cost push (ULC pass-through)
    pc2: float = 0.20               # Import price pass-through
    pc3: float = 0.05               # Output gap effect
    pc4: float = -0.10              # ECM adjustment speed
    pc5: float = 0.90               # Long-run ULC elasticity
    pc_vat: float = 0.38            # VAT pass-through to prices

    # --- Investment deflators ---
    pif1: float = 0.60              # Cost push for business investment prices
    pif2: float = 0.30              # Import price effect
    pif3: float = -0.08             # ECM speed
    pih1: float = 0.50              # Construction cost push
    pih2: float = 0.25              # Import price effect
    pih3: float = -0.06             # ECM speed
    pig1: float = 0.55              # Public investment price cost push
    pig2: float = 0.25              # Import price effect

    # --- Export prices ---
    px1: float = 0.40               # Domestic cost push
    px2: float = 0.55               # Foreign competitor price effect
    px3: float = -0.12              # ECM speed

    # --- Unit labour cost ---
    cost_w: float = 0.65            # Wage share in unit cost
    cost_pm: float = 0.35           # Import price share in unit cost

    # --- Export volume ECM ---
    x0: float = 0.002               # Constant
    x1: float = 0.80                # Foreign demand elasticity (short-run)
    x2: float = -0.30               # Price competitiveness (short-run)
    x3: float = -0.10               # ECM adjustment speed
    x4: float = 1.00                # Long-run foreign demand elasticity
    x5: float = -0.50               # Long-run price elasticity

    # --- Import volume ECM ---
    m0: float = 0.001               # Constant
    m1: float = 0.70                # Domestic demand elasticity (short-run)
    m2: float = 0.20                # Relative price effect (short-run)
    m3: float = -0.08               # ECM adjustment speed
    m4: float = 1.10                # Long-run demand elasticity
    m5: float = 0.40                # Long-run price elasticity

    # --- Public finance ---
    tax_prog: float = 1.10          # Tax progressivity (elasticity > 1)
    css_emp_rate: float = 0.30      # Baseline employer SSC rate
    css_house_rate: float = 0.13    # Baseline employee SSC rate
    vat_rate: float = 0.21          # Baseline VAT rate
    debt_rate: float = 0.03         # Average interest rate on public debt
    auto_stab: float = 0.50         # Automatic stabilizer strength

    # --- Fiscal multipliers (reduced-form calibration) ---
    vig_mult: float = 0.00022       # Public investment GDP multiplier (per mln)
    dth_mult: float = -0.00008      # Income tax GDP multiplier (per mln)
    tgh_mult: float = 0.20          # Transfer GDP multiplier (per grt %)
    ng_mult: float = 0.018          # Public employment GDP multiplier (per 1000)
    wgrr_mult: float = 0.08         # Public wage GDP multiplier (per %)
    wr_mult: float = 0.05           # Private wage correction GDP multiplier
    vat_gdp: float = -0.22          # VAT GDP sensitivity (per pp)
    cssemp_gdp: float = -0.12       # Employer SSC GDP sensitivity (per pp)
    csshouse_gdp: float = -0.07     # Employee SSC GDP sensitivity (per pp)

    # --- Persistence and feedback ---
    gdp_persistence: float = 0.35   # GDP shock persistence (AR1)
    okun: float = -0.30             # Okun coefficient (GDP gap -> UR)

    # --- Structural ---
    nairu: float = 0.08             # Structural unemployment rate (8%)
    pop_growth: float = 0.003       # Population growth rate
    nat_growth: float = 0.005       # Labour force growth rate
    pub_emp_share: float = 0.18     # Public employment share

    # --- Base year levels (2012, billions EUR unless noted) ---
    gdp_base: float = 387.0         # GDP at constant prices (bn EUR)
    k_base: float = 950.0           # Capital stock (bn EUR)
    tfp_base: float = 1.0           # TFP index (normalized)
    l_base: float = 4350.0          # Employment (thousands)
    nat_base: float = 4750.0        # Labour force (thousands)
    ng_base: float = 810.0          # Public employment (thousands)
    c_base: float = 200.0           # Private consumption (bn EUR)
    if_base: float = 50.0           # Business investment (bn EUR)
    ih_base: float = 22.0           # Housing investment (bn EUR)
    ig_base: float = 10.0           # Public investment (bn EUR)
    x_base: float = 320.0           # Exports (bn EUR)
    m_base: float = 310.0           # Imports (bn EUR)
    ydh_base: float = 210.0         # Household disposable income (bn EUR)
    w_base: float = 38.0            # Average wage (1000 EUR/year)
    pc_base: float = 1.0            # CPI index (normalized)
    deficit_base: float = -0.027    # Deficit/GDP ratio (negative = deficit)
    debt_gdp: float = 1.00          # Debt/GDP ratio
    r_nominal: float = 0.03         # Nominal interest rate

    # --- Foreign environment ---
    world_growth: float = 0.03      # World trade growth
    pm_growth: float = 0.015        # Import price growth
    pcomp_growth: float = 0.015     # Competitor price growth
