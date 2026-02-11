export interface InstrumentSpec {
  key: string;
  label: string;
  unit: string;
  default: number;
  min: number;
  max: number;
  description: string;
}

export interface KeyIndicators {
  years: number[];
  gdp_growth: number[];
  inflation: number[];
  deficit_ratio: number[];
  unemployment: number[];
}

export interface ConvergenceInfo {
  year: number;
  iterations: number;
  max_residual: number;
  status: string;
}

export interface SimulationResponse {
  name: string;
  years: number[];
  baseline: KeyIndicators;
  scenario: KeyIndicators;
  impacts: Record<string, Record<string, number>>;
  levels: Record<string, Record<string, number>>;
  convergence: ConvergenceInfo[];
  instruments: Record<string, number>;
}

export interface BaselineResponse {
  indicators: KeyIndicators;
  instruments: InstrumentSpec[];
}
