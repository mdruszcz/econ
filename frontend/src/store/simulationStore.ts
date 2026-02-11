import { create } from 'zustand';
import type { BaselineResponse, InstrumentSpec, SimulationResponse } from '../api/types';
import { getBaseline, runSimulation } from '../api/client';

interface SimulationStore {
  // Data
  instrumentSpecs: InstrumentSpec[];
  instrumentValues: Record<string, number>;
  baseline: BaselineResponse | null;
  result: SimulationResponse | null;

  // UI state
  loading: boolean;
  error: string | null;
  activeTab: number;

  // Actions
  setActiveTab: (tab: number) => void;
  setInstrumentValue: (key: string, value: number) => void;
  resetInstruments: () => void;
  applyPreset: (preset: string) => void;
  fetchBaseline: () => Promise<void>;
  simulate: () => Promise<void>;
}

export const useSimulationStore = create<SimulationStore>((set, get) => ({
  instrumentSpecs: [],
  instrumentValues: {},
  baseline: null,
  result: null,
  loading: false,
  error: null,
  activeTab: 0,

  setActiveTab: (tab) => set({ activeTab: tab }),

  setInstrumentValue: (key, value) =>
    set((s) => ({
      instrumentValues: { ...s.instrumentValues, [key]: value },
    })),

  resetInstruments: () => {
    const defaults: Record<string, number> = {};
    for (const spec of get().instrumentSpecs) {
      defaults[spec.key] = spec.default;
    }
    set({ instrumentValues: defaults, result: null });
  },

  applyPreset: (preset) => {
    const defaults: Record<string, number> = {};
    for (const spec of get().instrumentSpecs) {
      defaults[spec.key] = spec.default;
    }
    if (preset === 'stimulus') {
      defaults['VIG_X'] = 1000; // +1bn public investment
    }
    set({ instrumentValues: defaults });
  },

  fetchBaseline: async () => {
    set({ loading: true, error: null });
    try {
      const data = await getBaseline();
      const defaults: Record<string, number> = {};
      for (const spec of data.instruments) {
        defaults[spec.key] = spec.default;
      }
      set({
        baseline: data,
        instrumentSpecs: data.instruments,
        instrumentValues: defaults,
        loading: false,
      });
    } catch (e) {
      set({ error: (e as Error).message, loading: false });
    }
  },

  simulate: async () => {
    set({ loading: true, error: null });
    try {
      const result = await runSimulation(get().instrumentValues);
      set({ result, loading: false, activeTab: 1 });
    } catch (e) {
      set({ error: (e as Error).message, loading: false });
    }
  },
}));
