import { useSimulationStore } from '../../store/simulationStore';
import { IndicatorChart } from './IndicatorChart';

export function SimulationDashboard() {
  const { result } = useSimulationStore();

  if (!result) {
    return (
      <div className="dashboard-empty">
        <p>No simulation results yet. Configure instruments and click "Run Simulation".</p>
      </div>
    );
  }

  const { years, baseline, scenario, convergence } = result;
  const allConverged = convergence.every((c) => c.status === 'CONVERGED');

  return (
    <div className="dashboard">
      <div className="convergence-status" data-ok={allConverged}>
        {allConverged
          ? 'All years converged'
          : `Warning: some years did not converge`}
      </div>

      <div className="chart-grid">
        <IndicatorChart
          title="GDP Growth"
          years={years}
          baseline={baseline.gdp_growth}
          scenario={scenario.gdp_growth}
          yLabel="%"
        />
        <IndicatorChart
          title="Inflation"
          years={years}
          baseline={baseline.inflation}
          scenario={scenario.inflation}
          yLabel="%"
        />
        <IndicatorChart
          title="Deficit / GDP"
          years={years}
          baseline={baseline.deficit_ratio}
          scenario={scenario.deficit_ratio}
          yLabel="% of GDP"
        />
        <IndicatorChart
          title="Unemployment Rate"
          years={years}
          baseline={baseline.unemployment}
          scenario={scenario.unemployment}
          yLabel="%"
        />
      </div>

      <details className="convergence-details">
        <summary>Convergence Details</summary>
        <table>
          <thead>
            <tr><th>Year</th><th>Iterations</th><th>Max Residual</th><th>Status</th></tr>
          </thead>
          <tbody>
            {convergence.map((c) => (
              <tr key={c.year}>
                <td>{c.year}</td>
                <td>{c.iterations}</td>
                <td>{c.max_residual.toExponential(2)}</td>
                <td className={c.status === 'CONVERGED' ? 'ok' : 'warn'}>{c.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>
    </div>
  );
}
