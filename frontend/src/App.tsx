import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { DigitalTwinTab } from './components/DigitalTwinTab';
import { OverviewTab } from './components/OverviewTab';
import { LifecycleInspectorTab } from './components/LifecycleInspectorTab';
import { SimulationTab } from './components/SimulationTab';
import { ExperimentsTab } from './components/ExperimentsTab';
import { SecurityTab } from './components/SecurityTab';
import { DataExplorerTab } from './components/DataExplorerTab';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('digital_twin');

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col selection:bg-sky-500 selection:text-white">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'digital_twin' && <DigitalTwinTab />}
        {activeTab === 'overview' && <OverviewTab />}
        {activeTab === 'lifecycle' && <LifecycleInspectorTab />}
        {activeTab === 'simulation' && <SimulationTab />}
        {activeTab === 'experiments' && <ExperimentsTab />}
        {activeTab === 'security' && <SecurityTab />}
        {activeTab === 'data' && <DataExplorerTab />}
      </main>

      <footer className="border-t border-slate-900 bg-slate-950 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>CC-CIPAT &copy; Final Year Computer Engineering Project</span>
          <span className="font-mono text-slate-600">SimPy 4.1.2 | FastAPI 0.110 | React 18</span>
        </div>
      </footer>
    </div>
  );
};

export default App;
