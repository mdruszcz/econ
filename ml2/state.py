"""SimulationState: central data container with IODE-compatible operators."""

from __future__ import annotations

import math
from copy import deepcopy

import numpy as np
import pandas as pd

from ml2.types import VarName, Year


class SimulationState:
    """Wraps a pandas DataFrame (index=years, columns=variable names).

    Provides IODE-style operators: get, set, lag, dln, grt, d, mavg.
    """

    def __init__(self, df: pd.DataFrame) -> None:
        self._df = df.copy()
        self._df.index = self._df.index.astype(int)

    @property
    def years(self) -> list[Year]:
        return list(self._df.index)

    @property
    def sim_years(self) -> list[Year]:
        """Simulation years (excludes first year used for lags)."""
        return self.years[1:]

    @property
    def columns(self) -> list[VarName]:
        return list(self._df.columns)

    @property
    def df(self) -> pd.DataFrame:
        return self._df

    def get(self, var: VarName, t: Year) -> float:
        """Get variable value at year t."""
        return float(self._df.at[t, var])

    def set(self, var: VarName, t: Year, value: float) -> None:
        """Set variable value at year t."""
        self._df.at[t, var] = value

    def lag(self, var: VarName, t: Year, n: int = 1) -> float:
        """Get lagged value: var[t-n]."""
        return float(self._df.at[t - n, var])

    def dln(self, var: VarName, t: Year) -> float:
        """First difference of log: ln(X_t) - ln(X_{t-1})."""
        cur = self.get(var, t)
        prev = self.lag(var, t, 1)
        if cur <= 0 or prev <= 0:
            return 0.0
        return math.log(cur) - math.log(prev)

    def grt(self, var: VarName, t: Year) -> float:
        """Growth rate: (X_t - X_{t-1}) / X_{t-1} * 100."""
        prev = self.lag(var, t, 1)
        if prev == 0:
            return 0.0
        return (self.get(var, t) - prev) / prev * 100.0

    def d(self, var: VarName, t: Year) -> float:
        """First difference: X_t - X_{t-1}."""
        return self.get(var, t) - self.lag(var, t, 1)

    def mavg(self, var: VarName, t: Year, n: int = 3) -> float:
        """Moving average over n years ending at t."""
        vals = [self.get(var, t - i) for i in range(n) if (t - i) in self._df.index]
        return float(np.mean(vals)) if vals else 0.0

    def has_var(self, var: VarName) -> bool:
        return var in self._df.columns

    def add_var(self, var: VarName, default: float = 0.0) -> None:
        """Add a new variable with a default value for all years."""
        if var not in self._df.columns:
            self._df[var] = default

    def copy(self) -> SimulationState:
        """Deep copy of the state."""
        return SimulationState(self._df.copy(deep=True))

    def to_dict(self, variables: list[VarName] | None = None) -> dict[str, dict[Year, float]]:
        """Convert to nested dict {var: {year: value}}."""
        cols = variables if variables else self.columns
        return {
            var: {int(yr): float(self._df.at[yr, var]) for yr in self.years}
            for var in cols
            if var in self._df.columns
        }
