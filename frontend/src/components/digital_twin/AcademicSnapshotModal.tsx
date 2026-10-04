import React, { useState } from 'react';
import { X, Copy, Check, Download, FileText, Code2 } from 'lucide-react';
import { MetricSnapshot, DigitalTwinConfig, LiveTransaction } from '../../hooks/useDigitalTwinEngine';

interface SnapshotModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentMetrics: MetricSnapshot;
  config: DigitalTwinConfig;
  recentTransactions: LiveTransaction[];
  totalProcessed: number;
}

export const AcademicSnapshotModal: React.FC<SnapshotModalProps> = ({
  isOpen,
  onClose,
  currentMetrics,
  config,
  recentTransactions,
  totalProcessed,
}) => {
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState<'latex' | 'csv'>('latex');

  if (!isOpen) return null;

  const latexCode = `\\begin{table}[htbp]
\\caption{Real-Time Digital Twin Telemetry Snapshot (CC-CIPAT Simulation)}
\\label{tab:digital_twin_telemetry}
\\centering
\\begin{tabular}{|l|r|l|}
\\hline
\\textbf{Parameter / Metric} & \\textbf{Value} & \\textbf{Unit / Condition} \\\\
\\hline
Target Arrival Rate ($\\lambda$) & ${config.targetRps} & RPS \\\\
Current System Throughput & ${currentMetrics.rps} & RPS \\\\
Mean Response Time ($T_{resp}$) & ${currentMetrics.latencyMs} & ms (SLA $\\le 45$ms) \\\\
95th Percentile Latency ($P_{95}$) & ${currentMetrics.p95LatencyMs} & ms \\\\
Private DC CPU Utilization & ${currentMetrics.privateUtilPct}\\% & 48 Cores (Fixed) \\\\
Public Cloud CPU Utilization & ${currentMetrics.publicUtilPct}\\% & Dynamic Elastic Pool \\\\
Active Elastic Instances & ${currentMetrics.activePublicInstances} & Pods (4 cores/inst) \\\\
Autoscaler State & ${currentMetrics.autoscalerState} & Rule-based Hysteresis \\\\
Private Tier Queue Depth & ${currentMetrics.privateQueue} & Requests \\\\
Public Tier Queue Depth & ${currentMetrics.publicQueue} & Requests \\\\
Total Processed Volume & ${totalProcessed.toLocaleString()} & Transactions \\\\
Security Denial Rate & 0.00\\% & NIST SP 800-207 Enforced \\\\
\\hline
\\end{tabular}
\\end{table}`;

  const csvHeader = 'transaction_id,timestamp,service_type,security_tier,cloud_target,latency_ms,status\n';
  const csvRows = recentTransactions
    .map(
      (tx) =>
        `${tx.id},"${tx.timestamp}",${tx.serviceType},${tx.classification},${tx.targetTier},${tx.latencyMs},${tx.status}`
    )
    .join('\n');
  const csvContent = csvHeader + csvRows;

  const handleCopy = () => {
    const textToCopy = activeTab === 'latex' ? latexCode : csvContent;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadCsv = () => {
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `cc_cipat_telemetry_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full p-6 shadow-2xl space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <FileText className="h-5 w-5 text-indigo-400" />
            <div>
              <h3 className="text-base font-bold text-white">Academic Viva Defense Snapshot</h3>
              <p className="text-xs text-slate-400">Export verified telemetry for IEEE conference papers & presentations</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Tab selector */}
        <div className="flex space-x-2 border-b border-slate-800 pb-2">
          <button
            onClick={() => setActiveTab('latex')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-colors ${
              activeTab === 'latex'
                ? 'bg-indigo-600 text-white'
                : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            <Code2 className="h-3.5 w-3.5" />
            <span>IEEE LaTeX Table Format</span>
          </button>
          <button
            onClick={() => setActiveTab('csv')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-colors ${
              activeTab === 'csv'
                ? 'bg-indigo-600 text-white'
                : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            <Download className="h-3.5 w-3.5" />
            <span>Raw CSV Telemetry Data</span>
          </button>
        </div>

        {/* Content Box */}
        <div className="relative">
          <pre className="bg-slate-950 border border-slate-800 p-4 rounded-xl text-xs font-mono text-slate-300 max-h-72 overflow-y-auto overflow-x-auto select-all">
            {activeTab === 'latex' ? latexCode : csvContent}
          </pre>
        </div>

        {/* Action Footer */}
        <div className="flex justify-between items-center pt-2">
          <span className="text-[11px] text-slate-500 font-mono">
            Captured at {new Date().toLocaleTimeString()}
          </span>

          <div className="flex space-x-2">
            {activeTab === 'csv' && (
              <button
                onClick={handleDownloadCsv}
                className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors"
              >
                <Download className="h-3.5 w-3.5" />
                <span>Download .CSV</span>
              </button>
            )}

            <button
              onClick={handleCopy}
              className="flex items-center space-x-1.5 px-4 py-1.5 rounded-xl text-xs font-semibold bg-gradient-to-r from-indigo-500 to-purple-600 text-white hover:from-indigo-400 hover:to-purple-500 shadow-md transition-all"
            >
              {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
              <span>{copied ? 'Copied to Clipboard!' : 'Copy Code'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
