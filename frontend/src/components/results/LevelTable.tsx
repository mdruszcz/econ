import { useSimulationStore } from '../../store/simulationStore';

export function LevelTable() {
  const { result } = useSimulationStore();
  if (!result) return null;

  const { years, levels } = result;
  const vars = Object.keys(levels).sort();

  return (
    <div className="level-table-container">
      <h3>Projection Levels (Scenario)</h3>
      <div className="table-scroll">
        <table className="data-table">
          <thead>
            <tr>
              <th>Variable</th>
              {years.map((y) => <th key={y}>{y}</th>)}
            </tr>
          </thead>
          <tbody>
            {vars.map((varName) => (
              <tr key={varName}>
                <td className="var-name">{varName}</td>
                {years.map((y) => (
                  <td key={y}>
                    {(levels[varName]?.[String(y)] ?? 0).toFixed(2)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
