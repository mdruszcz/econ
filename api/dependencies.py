"""Engine singleton dependency."""

from functools import lru_cache

from ml2.engine import SimulationEngine


@lru_cache(maxsize=1)
def get_engine() -> SimulationEngine:
    """Create and cache a single SimulationEngine instance."""
    engine = SimulationEngine()
    engine.load_baseline()
    return engine
