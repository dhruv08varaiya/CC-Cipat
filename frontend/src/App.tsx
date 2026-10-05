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
    <div className="min-h-screen bg-[#090A0F] text-zinc-100 flex flex-col selection:bg-zinc-800 selection:text-white antialiased">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <main className="flex-1 max-w-[1400px] w-full mx-auto px-3 sm:px-4 lg:px-6 py-4">
        {activeTab === 'digital_twin' && <DigitalTwinTab />}
        {activeTab === 'lifecycle' && <LifecycleInspectorTab />}
        {activeTab === 'simulation' && <SimulationTab />}
        {activeTab === 'experiments' && <ExperimentsTab />}
        {activeTab === 'security' && <SecurityTab />}
        {activeTab === 'data' && <DataExplorerTab />}
        {activeTab === 'overview' && <OverviewTab />}
      </main>

      <footer className="border-t border-[#27272A] bg-[#090A0F] py-3 text-xs text-zinc-500">
        <div className="max-w-[1400px] mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span className="font-mono text-[11px] text-zinc-400">CC-CIPAT &bull; Computer Engineering Capstone</span>
          <span className="font-mono text-[11px] text-zinc-600">SimPy 4.1.2 &bull; FastAPI 0.110 &bull; React 18 (Industrial Monochrome)</span>
        </div>
      </footer>
    </div>
  );
};

export default App;
