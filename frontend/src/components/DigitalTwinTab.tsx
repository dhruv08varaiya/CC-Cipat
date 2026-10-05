import React, { useState } from 'react';
import { useDigitalTwinEngine } from '../hooks/useDigitalTwinEngine';
import { DigitalTwinControls } from './digital_twin/DigitalTwinControls';
import { DigitalTwinTopology } from './digital_twin/DigitalTwinTopology';
import { DigitalTwinOscilloscope } from './digital_twin/DigitalTwinOscilloscope';
import { DigitalTwinLedger } from './digital_twin/DigitalTwinLedger';
import { AcademicSnapshotModal } from './digital_twin/AcademicSnapshotModal';

export const DigitalTwinTab: React.FC = () => {
  const {
    config,
    setConfig,
    currentMetrics,
    history,
    recentTransactions,
    applyPreset,
  } = useDigitalTwinEngine();

  const [snapshotModalOpen, setSnapshotModalOpen] = useState(false);
  const [snapshotData, setSnapshotData] = useState({ latex: '', csv: '' });

  const handleOpenSnapshot = () => {
    const timestamp = new Date().toISOString();
    const latex = `\\begin{table}[htbp]
\\centering
\\caption{CC-CIPAT Live Digital Twin Telemetry Snapshot (Generated: ${timestamp})}
\\label{tab:digital_twin_telemetry}
\\begin{tabular}{lrr}
\\hline
\\textbf{Parameter / Metric} & \\textbf{Value} & \\textbf{Unit} \\\\
\\hline
Target Arrival Rate ($\\lambda$) & ${config.targetRps} & RPS \\\\
Current Measured RPS & ${currentMetrics.rps} & RPS \\\\
Mean Transaction Latency ($E[W]$) & ${currentMetrics.latencyMs.toFixed(2)} & ms \\\\
P95 Transaction Latency & ${currentMetrics.p95LatencyMs.toFixed(2)} & ms \\\\
Private DC Queue Depth ($L_{q,priv}$) & ${currentMetrics.privateQueue} & reqs \\\\
Public Cloud Queue Depth ($L_{q,pub}$) & ${currentMetrics.publicQueue} & reqs \\\\
Private Core Utilization ($\\rho_{priv}$) & ${currentMetrics.privateUtilPct.toFixed(1)}\\% & \\% \\\\
Public Cloud Utilization ($\\rho_{pub}$) & ${currentMetrics.publicUtilPct.toFixed(1)}\\% & \\% \\\\
Active Elastic Instances ($c_{pub}$) & ${currentMetrics.activePublicInstances} & Pods \\\\
Autoscaler State Machine & \\texttt{${currentMetrics.autoscalerState}} & -- \\\\
Total Dropped Requests & ${currentMetrics.droppedRequests} & reqs \\\\
\\hline
\\end{tabular}
\\end{table}`;

    const csvHeaders = 'timestamp_sec,measured_rps,mean_latency_ms,p95_latency_ms,private_queue,public_queue,private_util_pct,public_util_pct,active_pods,dropped_requests\n';
    const csvRows = history.slice(-20).map(pt => 
      `${pt.timeSec.toFixed(1)},${pt.rps},${pt.latencyMs.toFixed(2)},${pt.p95LatencyMs.toFixed(2)},${pt.privateQueue},${pt.publicQueue},${pt.privateUtilPct.toFixed(1)},${pt.publicUtilPct.toFixed(1)},${pt.activePublicInstances},${pt.droppedRequests}`
    ).join('\n');

    setSnapshotData({ latex, csv: csvHeaders + csvRows });
    setSnapshotModalOpen(true);
  };

  const isAnyChaos = config.chaosCoreDrop || config.chaosNetworkSpike || config.chaosDbLock || config.chaosAttackProbe;

  return (
    <div className="space-y-3">
      {/* Top Telemetry KPI Ribbon */}
      <div className="bg-[#12131A] border border-[#27272A] rounded-md p-2.5 flex flex-wrap items-center justify-between gap-3 font-mono text-xs">
        <div className="flex items-center space-x-2">
          <span className="font-bold text-zinc-100">TELEMETRY DECK</span>
          <span className="text-[10px] text-zinc-500">&bull; Live Hybrid Traffic</span>
        </div>

        <div className="flex items-center space-x-3 sm:space-x-6">
          <div>
            <span className="text-[10px] text-zinc-500 block">Throughput</span>
            <span className="text-zinc-200 font-bold">{currentMetrics.rps.toLocaleString()} RPS</span>
          </div>
          <div>
            <span className="text-[10px] text-zinc-500 block">Mean Latency</span>
            <span className="text-sky-400 font-bold">{currentMetrics.latencyMs.toFixed(2)} ms</span>
          </div>
          <div>
            <span className="text-[10px] text-zinc-500 block">Queue Depth</span>
            <span className="text-zinc-200 font-bold">{currentMetrics.totalQueue} reqs</span>
          </div>
          <div>
            <span className="text-[10px] text-zinc-500 block">Elastic Tier</span>
            <span className="text-emerald-400 font-bold">{currentMetrics.activePublicInstances} Pods</span>
          </div>
        </div>
      </div>

      {/* Unified Simulation Toolbar */}
      <DigitalTwinControls
        config={config}
        setConfig={setConfig}
        applyPreset={applyPreset}
        onOpenSnapshot={handleOpenSnapshot}
      />

      {/* Interactive SVG Service Mesh Topology */}
      <DigitalTwinTopology
        metrics={currentMetrics}
        isPaused={config.isPaused}
        isChaos={isAnyChaos}
      />

      {/* Bottom Split Telemetry Pane */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-3">
        <div className="lg:col-span-6 min-h-[220px]">
          <DigitalTwinOscilloscope history={history} />
        </div>
        <div className="lg:col-span-6 min-h-[220px]">
          <DigitalTwinLedger transactions={recentTransactions} />
        </div>
      </div>

      {/* IEEE LaTeX / CSV Modal */}
      <AcademicSnapshotModal
        isOpen={snapshotModalOpen}
        onClose={() => setSnapshotModalOpen(false)}
        latexCode={snapshotData.latex}
        csvData={snapshotData.csv}
      />
    </div>
  );
};
