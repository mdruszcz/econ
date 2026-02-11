"""Instrument endpoints: GET /instruments."""

from fastapi import APIRouter, Depends

from api.dependencies import get_engine
from api.schemas import InstrumentSpecResponse
from ml2.engine import SimulationEngine

router = APIRouter()


@router.get("/instruments", response_model=list[InstrumentSpecResponse])
def get_instruments(
    engine: SimulationEngine = Depends(get_engine),
) -> list[InstrumentSpecResponse]:
    """Get all available policy instrument specifications."""
    return engine.get_instrument_specs()
