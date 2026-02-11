import { useSimulationStore } from '../../store/simulationStore';
import { InstrumentRow } from './InstrumentRow';

export function InstrumentGrid() {
  const { instrumentSpecs, instrumentValues, setInstrumentValue, resetInstruments, applyPreset, simulate, loading, baseline } = useSimulationStore();

  return (
    <div className="instrument-panel">
      <div className="instrument-header">
        <h2>Policy Instruments</h2>
        <div className="preset-buttons">
          <button onClick={resetInstruments} disabled={loading}>Reset to Baseline</button>
          <button onClick={() => applyPreset('stimulus')} disabled={loading}>+1bn Stimulus</button>
        </div>
      </div>

      <div className="instrument-grid">
        {instrumentSpecs.map((spec) => (
          <InstrumentRow
            key={spec.key}
            spec={spec}
            value={instrumentValues[spec.key] ?? spec.default}
            onChange={(v) => setInstrumentValue(spec.key, v)}
          />
        ))}
      </div>

      <div className="simulate-actions">
        <button className="btn-primary" onClick={simulate} disabled={loading}>
          {loading ? 'Simulating...' : 'Run Simulation'}
        </button>
      </div>

      {baseline && (
        <div className="baseline-preview">
          <h3>Baseline Preview</h3>
          <table>
            <thead>
              <tr>
                <th>Indicator</th>
                {baseline.indicators.years.map((y) => <th key={y}>{y}</th>)}
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>GDP Growth (%)</td>
                {baseline.indicators.gdp_growth.map((v, i) => <td key={i}>{v.toFixed(1)}</td>)}
              </tr>
              <tr>
                <td>Inflation (%)</td>
                {baseline.indicators.inflation.map((v, i) => <td key={i}>{v.toFixed(1)}</td>)}
              </tr>
              <tr>
                <td>Deficit/GDP (%)</td>
                {baseline.indicators.deficit_ratio.map((v, i) => <td key={i}>{v.toFixed(1)}</td>)}
              </tr>
              <tr>
                <td>Unemployment (%)</td>
                {baseline.indicators.unemployment.map((v, i) => <td key={i}>{v.toFixed(1)}</td>)}
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
