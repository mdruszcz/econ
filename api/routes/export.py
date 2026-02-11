"""Export endpoints: CSV and Excel download."""

import io

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from api.dependencies import get_engine
from api.schemas import SimulationRequest
from ml2.engine import SimulationEngine

router = APIRouter()


def _build_csv(engine: SimulationEngine, instruments: dict[str, float], name: str) -> str:
    """Run simulation and format results as CSV."""
    result = engine.simulate(instrument_values=instruments or None, name=name)

    lines = [f"# ML2 Simulation: {result.name}"]
    lines.append(f"# Years: {result.years[0]}-{result.years[-1]}")
    lines.append("")

    # Key indicators
    lines.append("Indicator," + ",".join(str(y) for y in result.years))
    for label, vals in [
        ("GDP Growth (%) - Baseline", result.baseline_indicators.gdp_growth),
        ("GDP Growth (%) - Scenario", result.scenario_indicators.gdp_growth),
        ("Inflation (%) - Baseline", result.baseline_indicators.inflation),
        ("Inflation (%) - Scenario", result.scenario_indicators.inflation),
        ("Deficit/GDP (%) - Baseline", result.baseline_indicators.deficit_ratio),
        ("Deficit/GDP (%) - Scenario", result.scenario_indicators.deficit_ratio),
        ("Unemployment (%) - Baseline", result.baseline_indicators.unemployment),
        ("Unemployment (%) - Scenario", result.scenario_indicators.unemployment),
    ]:
        lines.append(label + "," + ",".join(f"{v:.2f}" for v in vals))

    lines.append("")
    lines.append("# Impacts (% deviation from baseline)")
    for var, yr_dict in result.impacts.items():
        vals = [yr_dict.get(y, 0.0) for y in result.years]
        if any(abs(v) > 0.001 for v in vals):
            lines.append(var + "," + ",".join(f"{v:.4f}" for v in vals))

    return "\n".join(lines)


@router.post("/export/csv")
def export_csv(
    request: SimulationRequest,
    engine: SimulationEngine = Depends(get_engine),
) -> StreamingResponse:
    """Export simulation results as CSV."""
    try:
        csv_content = _build_csv(engine, request.instruments, request.name)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return StreamingResponse(
        io.BytesIO(csv_content.encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=ml2_{request.name}.csv"},
    )


@router.post("/export/excel")
def export_excel(
    request: SimulationRequest,
    engine: SimulationEngine = Depends(get_engine),
) -> StreamingResponse:
    """Export simulation results as Excel."""
    import pandas as pd

    try:
        result = engine.simulate(instrument_values=request.instruments or None, name=request.name)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        # Key indicators sheet
        ind_data = {
            "Year": result.years,
            "GDP Growth (Baseline)": result.baseline_indicators.gdp_growth,
            "GDP Growth (Scenario)": result.scenario_indicators.gdp_growth,
            "Inflation (Baseline)": result.baseline_indicators.inflation,
            "Inflation (Scenario)": result.scenario_indicators.inflation,
            "Deficit/GDP (Baseline)": result.baseline_indicators.deficit_ratio,
            "Deficit/GDP (Scenario)": result.scenario_indicators.deficit_ratio,
            "Unemployment (Baseline)": result.baseline_indicators.unemployment,
            "Unemployment (Scenario)": result.scenario_indicators.unemployment,
        }
        pd.DataFrame(ind_data).to_excel(writer, sheet_name="Indicators", index=False)

        # Impacts sheet
        impact_rows = []
        for var, yr_dict in result.impacts.items():
            vals = [yr_dict.get(y, 0.0) for y in result.years]
            if any(abs(v) > 0.001 for v in vals):
                impact_rows.append({"Variable": var, **{str(y): v for y, v in zip(result.years, vals)}})
        if impact_rows:
            pd.DataFrame(impact_rows).to_excel(writer, sheet_name="Impacts", index=False)

        # Levels sheet
        for var, yr_dict in result.levels.items():
            pass  # included in impacts sheet context

    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=ml2_{request.name}.xlsx"},
    )
