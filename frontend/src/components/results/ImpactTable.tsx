import { useSimulationStore } from '../../store/simulationStore';

export function ImpactTable() {
  const { result } = useSimulationStore();
  if (!result) return null;

  const { years, impacts } = result;

  // Filter to variables with non-trivial impacts
  const significantVars = Object.entries(impacts)
    .filter(([, yrDict]) =>
      Object.values(yrDict).some((v) => Math.abs(v) > 0.001)
    )
    .sort(([a], [b]) => a.localeCompare(b));

  return (
    <div className="impact-table-container">
      <h3>Impact vs Baseline (% deviation or pp)</h3>
      <div className="table-scroll">
        <table className="data-table">
          <thead>
            <tr>
              <th>Variable</th>
              {years.map((y) => <th key={y}>{y}</th>)}
            </tr>
          </thead>
          <tbody>
            {significantVars.map(([varName, yrDict]) => (
              <tr key={varName}>
                <td className="var-name">{varName}</td>
                {years.map((y) => {
                  const val = yrDict[String(y)] ?? 0;
                  return (
                    <td key={y} className={val > 0 ? 'positive' : val < 0 ? 'negative' : ''}>
                      {val.toFixed(2)}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
