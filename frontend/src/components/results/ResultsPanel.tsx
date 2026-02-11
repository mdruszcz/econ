import { useState } from 'react';
import { useSimulationStore } from '../../store/simulationStore';
import { ImpactTable } from './ImpactTable';
import { LevelTable } from './LevelTable';
import { ExportButtons } from './ExportButtons';

export function ResultsPanel() {
  const { result } = useSimulationStore();
  const [subTab, setSubTab] = useState<'policy' | 'impact' | 'projection'>('impact');

  if (!result) {
    return (
      <div className="results-empty">
        <p>Run a simulation to see detailed results.</p>
      </div>
    );
  }

  return (
    <div className="results-panel">
      <div className="sub-tabs">
        <button className={subTab === 'policy' ? 'active' : ''} onClick={() => setSubTab('policy')}>
          Policy
        </button>
        <button className={subTab === 'impact' ? 'active' : ''} onClick={() => setSubTab('impact')}>
          Impact
        </button>
        <button className={subTab === 'projection' ? 'active' : ''} onClick={() => setSubTab('projection')}>
          Projection
        </button>
      </div>

      {subTab === 'policy' && (
        <div className="policy-summary">
          <h3>Policy Instruments (Applied Values)</h3>
          <table className="data-table">
            <thead>
              <tr><th>Instrument</th><th>Value</th></tr>
            </thead>
            <tbody>
              {Object.entries(result.instruments).map(([key, val]) => (
                <tr key={key}>
                  <td>{key}</td>
                  <td>{val}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {subTab === 'impact' && <ImpactTable />}
      {subTab === 'projection' && <LevelTable />}

      <ExportButtons />
    </div>
  );
}
