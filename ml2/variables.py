"""Variable classification and baseline data loading."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from ml2.state import SimulationState
from ml2.types import VarName

# Variable classification sets
EXOGENOUS: set[VarName] = {
    "TFP_", "NAT_", "NG_", "XWORLD_", "PCOMP_", "PM_",
    "RNOM_", "RMORT_", "ITPC0R_", "CSSFR_", "CSSHR_",
    "IG_", "TGH_", "DS_",
}

INTERDEPENDENT: set[VarName] = {
    "K_", "Y_", "YSTAR_", "YGAP_", "ZKF_",
    "LH_", "L_", "U_", "UR_",
    "W_", "WG_", "ULC_", "COST_",
    "PC_", "PIF_", "PIH_", "PIG_", "PX_",
    "RREAL_", "PROFIT_", "CG_", "YDH_",
    "C_", "IF_", "IH_", "DD_",
    "X_", "M_", "GDP_", "PGDP_", "GDPN_",
    "GRECEIPTS_", "GEXPENSE_", "D_", "B_",
}

POST_RECURSIVE: set[VarName] = {
    "I_", "PROD_", "WB_", "DR_", "BR_",
    "XN_", "MN_", "TB_", "TBR_",
}

# Key indicator variables for dashboard display
KEY_INDICATORS: list[VarName] = ["GDP_", "PC_", "DR_", "UR_"]

DATA_DIR = Path(__file__).parent.parent / "data" / "baseline"


class BaselineDataLoader:
    """Loads baseline variable time series and scalars from JSON files."""

    def __init__(self, data_dir: Path | None = None) -> None:
        self._data_dir = data_dir or DATA_DIR

    def load_state(self) -> SimulationState:
        """Load baseline variables into a SimulationState."""
        path = self._data_dir / "baseline_variables.json"
        with open(path) as f:
            data = json.load(f)

        # Convert to DataFrame: {var: {year_str: value}} -> DataFrame
        records: dict[str, dict[int, float]] = {}
        for var, series in data.items():
            records[var] = {int(yr): float(val) for yr, val in series.items()}

        df = pd.DataFrame(records)
        df.index.name = "year"
        return SimulationState(df)

    def load_scalars(self) -> dict[str, float]:
        """Load scalar parameters from JSON."""
        path = self._data_dir / "scalars.json"
        with open(path) as f:
            return json.load(f)
