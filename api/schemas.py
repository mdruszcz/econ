"""Pydantic request/response models for the API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    name: str = Field(default="Scenario", max_length=100)
    instruments: dict[str, float] = Field(default_factory=dict)


class KeyIndicatorsResponse(BaseModel):
    years: list[int]
    gdp_growth: list[float]
    inflation: list[float]
    deficit_ratio: list[float]
    unemployment: list[float]


class ConvergenceInfo(BaseModel):
    year: int
    iterations: int
    max_residual: float
    status: str


class SimulationResponse(BaseModel):
    name: str
    years: list[int]
    baseline: KeyIndicatorsResponse
    scenario: KeyIndicatorsResponse
    impacts: dict[str, dict[str, float]]
    levels: dict[str, dict[str, float]]
    convergence: list[ConvergenceInfo]
    instruments: dict[str, float]


class InstrumentSpecResponse(BaseModel):
    key: str
    label: str
    unit: str
    default: float
    min: float
    max: float
    description: str


class BaselineResponse(BaseModel):
    indicators: KeyIndicatorsResponse
    instruments: list[InstrumentSpecResponse]


class ErrorResponse(BaseModel):
    detail: str
