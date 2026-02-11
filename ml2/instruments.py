"""Policy instrument definitions and application logic."""

from __future__ import annotations

from dataclasses import dataclass

from ml2.state import SimulationState
from ml2.types import VarName, Year


@dataclass(frozen=True)
class InstrumentSpec:
    key: str              # Instrument variable name (e.g. "VIG_X")
    label: str            # Human-readable label
    unit: str             # Unit description
    default: float        # Baseline value
    min_val: float        # Minimum allowed
    max_val: float        # Maximum allowed
    description: str      # Detailed description


INSTRUMENTS: list[InstrumentSpec] = [
    InstrumentSpec(
        key="VIG_X",
        label="Public Investments",
        unit="mln EUR (change)",
        default=0.0,
        min_val=-2000.0,
        max_val=6000.0,
        description="Change in public investment expenditure (millions EUR, constant prices)",
    ),
    InstrumentSpec(
        key="ITPC0R_X",
        label="VAT Rate",
        unit="% (level)",
        default=21.0,
        min_val=15.0,
        max_val=27.0,
        description="Standard VAT rate on consumption (%)",
    ),
    InstrumentSpec(
        key="DTH_X",
        label="Income Tax Receipts",
        unit="mln EUR (change)",
        default=0.0,
        min_val=-10000.0,
        max_val=10000.0,
        description="Change in personal income tax receipts (millions EUR)",
    ),
    InstrumentSpec(
        key="CSSFR_X",
        label="Employer SSC Rate",
        unit="% of wages (level)",
        default=30.0,
        min_val=25.0,
        max_val=40.0,
        description="Employer social security contribution rate (% of gross wages)",
    ),
    InstrumentSpec(
        key="CSSHR_X",
        label="Employee SSC Rate",
        unit="% of wages (level)",
        default=13.0,
        min_val=10.0,
        max_val=20.0,
        description="Employee social security contribution rate (% of gross wages)",
    ),
    InstrumentSpec(
        key="TGH_X",
        label="Transfers to Households",
        unit="% (growth rate)",
        default=0.0,
        min_val=-5.0,
        max_val=5.0,
        description="Additional growth rate of transfers to households (%, constant prices)",
    ),
    InstrumentSpec(
        key="WR_X",
        label="Private Wage Correction",
        unit="pp",
        default=0.0,
        min_val=-2.0,
        max_val=2.0,
        description="Correction to private sector nominal wage growth (percentage points)",
    ),
    InstrumentSpec(
        key="WGRR_X",
        label="Public Real Wage Growth",
        unit="% p.a.",
        default=0.0,
        min_val=-2.0,
        max_val=5.0,
        description="Real wage growth in the public sector (% per year)",
    ),
    InstrumentSpec(
        key="NG_X",
        label="Public Employment",
        unit="thousands (change)",
        default=0.0,
        min_val=-40.0,
        max_val=40.0,
        description="Change in public sector employment (thousands of persons)",
    ),
    InstrumentSpec(
        key="ZX_X",
        label="Indexation Correction",
        unit="pp",
        default=0.0,
        min_val=-2.0,
        max_val=0.0,
        description="Change in automatic wage indexation mechanism (percentage points)",
    ),
]

INSTRUMENT_MAP: dict[str, InstrumentSpec] = {i.key: i for i in INSTRUMENTS}


def apply_instruments(
    state: SimulationState,
    instrument_values: dict[str, float],
    sim_years: list[Year],
) -> None:
    """Write instrument values into the simulation state for all sim years.

    Instruments that map to model variables:
    - ITPC0R_X -> ITPC0R_ (level, so ITPC0R_ = ITPC0R_X)
    - CSSFR_X -> CSSFR_ (level, CSSFR_ = CSSFR_X / 100)
    - CSSHR_X -> CSSHR_ (level, CSSHR_ = CSSHR_X / 100)
    - Others are read directly from state by equations
    """
    for year in sim_years:
        for key, value in instrument_values.items():
            if not state.has_var(key):
                state.add_var(key, 0.0)
            state.set(key, year, value)

        # Direct mappings
        if "ITPC0R_X" in instrument_values:
            state.set("ITPC0R_", year, instrument_values["ITPC0R_X"])
        if "CSSFR_X" in instrument_values:
            state.set("CSSFR_", year, instrument_values["CSSFR_X"] / 100.0)
        if "CSSHR_X" in instrument_values:
            state.set("CSSHR_", year, instrument_values["CSSHR_X"] / 100.0)


def get_default_instruments() -> dict[str, float]:
    """Return default (baseline) instrument values."""
    return {i.key: i.default for i in INSTRUMENTS}


def validate_instruments(values: dict[str, float]) -> list[str]:
    """Validate instrument values, return list of error messages."""
    errors = []
    for key, val in values.items():
        spec = INSTRUMENT_MAP.get(key)
        if spec is None:
            errors.append(f"Unknown instrument: {key}")
            continue
        if val < spec.min_val or val > spec.max_val:
            errors.append(f"{key}: {val} out of range [{spec.min_val}, {spec.max_val}]")
    return errors
