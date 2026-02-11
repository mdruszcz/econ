import { useEffect } from 'react';
import { useSimulationStore } from './store/simulationStore';
import { InstrumentGrid } from './components/instruments/InstrumentGrid';
import { SimulationDashboard } from './components/dashboard/SimulationDashboard';
import { ResultsPanel } from './components/results/ResultsPanel';
import './App.css';

const TABS = ['Instruments', 'Dashboard', 'Results'] as const;

function App() {
  const { activeTab, setActiveTab, fetchBaseline, error, loading } = useSimulationStore();

  useEffect(() => {
    fetchBaseline();
  }, [fetchBaseline]);

  return (
    <div className="app">
      <header className="app-header">
        <h1>ML2 Belgian Economy Simulator</h1>
        <p>Macroeconomic policy simulation engine</p>
      </header>

      {error && <div className="error-banner">Error: {error}</div>}

      <nav className="tab-bar">
        {TABS.map((tab, i) => (
          <button
            key={tab}
            className={`tab ${activeTab === i ? 'active' : ''}`}
            onClick={() => setActiveTab(i)}
          >
            {tab}
          </button>
        ))}
        {loading && <span className="loading-indicator">Loading...</span>}
      </nav>

      <main className="tab-content">
        {activeTab === 0 && <InstrumentGrid />}
        {activeTab === 1 && <SimulationDashboard />}
        {activeTab === 2 && <ResultsPanel />}
      </main>
    </div>
  );
}

export default App;
