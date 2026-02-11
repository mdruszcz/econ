import { useSimulationStore } from '../../store/simulationStore';
import { downloadCsv, downloadExcel } from '../../api/client';

export function ExportButtons() {
  const { result, instrumentValues } = useSimulationStore();
  if (!result) return null;

  return (
    <div className="export-buttons">
      <button onClick={() => downloadCsv(instrumentValues, result.name)}>
        Export CSV
      </button>
      <button onClick={() => downloadExcel(instrumentValues, result.name)}>
        Export Excel
      </button>
    </div>
  );
}
