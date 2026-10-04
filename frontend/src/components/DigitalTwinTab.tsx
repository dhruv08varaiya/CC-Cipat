import React, { useState } from 'react';
import { useDigitalTwinEngine } from '../hooks/useDigitalTwinEngine';
import { DigitalTwinTopology } from './digital_twin/DigitalTwinTopology';
import { DigitalTwinOscilloscope } from './digital_twin/DigitalTwinOscilloscope';
import { DigitalTwinLedger } from './digital_twin/DigitalTwinLedger';
import { DigitalTwinControls } from './digital_twin/DigitalTwinControls';
import { AcademicSnapshotModal } from './digital_twin/AcademicSnapshotModal';
import { Radio, Activity, Cpu, Server, Zap } from 'lucide-react';

export const DigitalTwinTab: React.FC = () => {
  const {
    config,
    setConfig,
    applyPreset,
    currentMetrics,
    history,
    recentTransactions,
    totalProcessed,
    totalDropped,
  } = useDigitalTwinEngine();

  const [isSnapshotOpen, setIsSnapshotOpen] = useState(false);

  return (
    <div className="space-y-5 animate-fade-in">
      {/* Top Banner KPI Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2.5">
            <div className="h-8 w-8 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-sky-500/20">
              <Radio className="h-4 w-4 animate-pulse" />
            </div>
            <h1 className="text-xl font-bold text-white tracking-tight">Living Cloud Digital Twin</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Live Interactive Engine
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Real-time interactive banking cloud traffic generator, multi-tier queue dynamics & chaos engineering lab
          </p>
        </div>

        {/* Quick KPI Stat Pills */}
        <div className="flex items-center flex-wrap gap-2 text-xs">
          <div className="bg-slate-950 border border-slate-800 px-3 py-1.5 rounded-xl">
            <span className="text-slate-400 text-[10px] block">Live Throughput</span>
            <span className="font-mono font-bold text-white">{currentMetrics.rps.toLocaleString()} RPS</span>
          </div>

          <div className="bg-slate-950 border border-slate-800 px-3 py-1.5 rounded-xl">
            <span className="text-slate-400 text-[10px] block">Mean Latency</span>
            <span className="font-mono font-bold text-sky-400">{currentMetrics.latencyMs} ms</span>
          </div>

          <div className="bg-slate-950 border border-slate-800 px-3 py-1.5 rounded-xl">
            <span className="text-slate-400 text-[10px] block">Total Queue Depth</span>
            <span className={`font-mono font-bold ${currentMetrics.totalQueue > 50 ? 'text-amber-400' : 'text-slate-200'}`}>
              {currentMetrics.totalQueue} reqs
            </span>
          </div>

          <div className="bg-slate-950 border border-slate-800 px-3 py-1.5 rounded-xl">
            <span className="text-slate-400 text-[10px] block">Elastic Pods</span>
            <span className="font-mono font-bold text-purple-300">{currentMetrics.activePublicInstances} Pods</span>
          </div>
        </div>
      </div>

      {/* 1. Interactive Glass-Box Controls */}
      <DigitalTwinControls
        config={config}
        setConfig={setConfig}
        applyPreset={applyPreset}
        onOpenSnapshot={() => setIsSnapshotOpen(true)}
      />

      {/* 2. Cluster Topology & Node Meters */}
      <DigitalTwinTopology metrics={currentMetrics} config={config} />

      {/* 3. Rolling Oscilloscope Waveforms */}
      <DigitalTwinOscilloscope history={history} currentMetrics={currentMetrics} />

      {/* 4. Streaming Transaction Ledger */}
      <DigitalTwinLedger
        transactions={recentTransactions}
        totalProcessed={totalProcessed}
        totalDropped={totalDropped}
      />

      {/* Academic Viva Snapshot Modal */}
      <AcademicSnapshotModal
        isOpen={isSnapshotOpen}
        onClose={() => setIsSnapshotOpen(false)}
        currentMetrics={currentMetrics}
        config={config}
        recentTransactions={recentTransactions}
        totalProcessed={totalProcessed}
      />
    </div>
  );
};
