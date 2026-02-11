"""Simulation endpoints: POST /simulate, GET /baseline."""

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_engine
from api.schemas import (
    BaselineResponse,
    ConvergenceInfo,
    KeyIndicatorsResponse,
    SimulationRequest,
    SimulationResponse,
)
from ml2.engine import SimulationEngine

router = APIRouter()


@router.post("/simulate", response_model=SimulationResponse)
def run_simulation(
    request: SimulationRequest,
    engine: SimulationEngine = Depends(get_engine),
) -> SimulationResponse:
    """Run a policy simulation with given instrument values."""
    try:
        result = engine.simulate(
            instrument_values=request.instruments if request.instruments else None,
            name=request.name,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Convert int year keys to string for JSON serialization
    impacts_str = {
        var: {str(yr): val for yr, val in yr_dict.items()}
        for var, yr_dict in result.impacts.items()
    }
    levels_str = {
        var: {str(yr): val for yr, val in yr_dict.items()}
        for var, yr_dict in result.levels.items()
    }

    return SimulationResponse(
        name=result.name,
        years=result.years,
        baseline=KeyIndicatorsResponse(
            years=result.baseline_indicators.years,
            gdp_growth=result.baseline_indicators.gdp_growth,
            inflation=result.baseline_indicators.inflation,
            deficit_ratio=result.baseline_indicators.deficit_ratio,
            unemployment=result.baseline_indicators.unemployment,
        ),
        scenario=KeyIndicatorsResponse(
            years=result.scenario_indicators.years,
            gdp_growth=result.scenario_indicators.gdp_growth,
            inflation=result.scenario_indicators.inflation,
            deficit_ratio=result.scenario_indicators.deficit_ratio,
            unemployment=result.scenario_indicators.unemployment,
        ),
        impacts=impacts_str,
        levels=levels_str,
        convergence=[
            ConvergenceInfo(**c) for c in result.convergence
        ],
        instruments=result.instruments,
    )


@router.get("/baseline", response_model=BaselineResponse)
def get_baseline(
    engine: SimulationEngine = Depends(get_engine),
) -> BaselineResponse:
    """Get baseline indicators and instrument specifications."""
    indicators = engine.get_baseline_indicators()
    instruments = engine.get_instrument_specs()

    return BaselineResponse(
        indicators=KeyIndicatorsResponse(
            years=indicators.years,
            gdp_growth=indicators.gdp_growth,
            inflation=indicators.inflation,
            deficit_ratio=indicators.deficit_ratio,
            unemployment=indicators.unemployment,
        ),
        instruments=instruments,
    )
