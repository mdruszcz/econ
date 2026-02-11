import type { BaselineResponse, SimulationResponse } from './types';

const BASE_URL = '/api';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function getBaseline(): Promise<BaselineResponse> {
  return fetchJson<BaselineResponse>('/baseline');
}

export async function runSimulation(
  instruments: Record<string, number>,
  name = 'Scenario',
): Promise<SimulationResponse> {
  return fetchJson<SimulationResponse>('/simulate', {
    method: 'POST',
    body: JSON.stringify({ name, instruments }),
  });
}

export function exportCsvUrl(instruments: Record<string, number>, name = 'Scenario'): string {
  // For CSV/Excel we POST, so we return the endpoint and let the component handle it
  return `${BASE_URL}/export/csv`;
}

export async function downloadCsv(instruments: Record<string, number>, name = 'Scenario'): Promise<void> {
  const res = await fetch(`${BASE_URL}/export/csv`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, instruments }),
  });
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `ml2_${name}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

export async function downloadExcel(instruments: Record<string, number>, name = 'Scenario'): Promise<void> {
  const res = await fetch(`${BASE_URL}/export/excel`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, instruments }),
  });
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `ml2_${name}.xlsx`;
  a.click();
  URL.revokeObjectURL(url);
}
