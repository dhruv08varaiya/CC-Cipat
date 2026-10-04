import React, { useState, useEffect } from 'react';
import { 
  Play, 
  RefreshCw, 
  Sliders, 
  Activity, 
  Cpu, 
  Server, 
  TrendingUp, 
  AlertTriangle 
} from 'lucide-react';
import { 
  fetchWorkloads, 
  runSimulation, 
  WorkloadItem, 
  SimulationResult 
} from '../api/client';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';

export const SimulationTab: React.FC = () => {
  const [workloads, setWorkloads] = useState<WorkloadItem[]>([]);
  const [selectedWorkload, setSelectedWorkload] = useState('W1');
  const [architecture, setArchitecture] = useState('hybrid_autoscaling');
  const [maxEvents, setMaxEvents] = useState(1000);
  const [seed, setSeed] = useState(42);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<SimulationResult | null>(null);

  useEffect(() => {
    fetchWorkloads()
      .then((data) => setWorkloads(data))
      .catch((err) => console.error('Failed to load workloads:', err));
  }, []);

  const handleRunSimulation = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await runSimulation({
        architecture,
        workload_id: selectedWorkload,
        seed,
        max_events: maxEvents,
        autoscaling_enabled: architecture === 'hybrid_autoscaling',
      });
      setResults(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Simulation run failed');
    } finally {
      setLoading(false);
    }
  };

  const summary = results?.results?.summary;
  const timeSeries = results?.results?.time_series || [];
  const scalingEvents = results?.results?.scaling_events || [];

  return (
    <div className="space-y-6">
      {/* Control Panel */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-800">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-sky-500/10 text-sky-400 border border-sky-500/20">
              <Sliders className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">Discrete-Event Simulation Harness</h2>
              <p className="text-xs text-slate-400">Configure parameters and execute SimPy engine runs</p>
            </div>
          </div>
          <button
            onClick={handleRunSimulation}
            disabled={loading}
            className={`flex items-center space-x-2 px-5 py-2.5 rounded-xl font-semibold text-sm transition-all shadow-lg ${
              loading
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-sky-500 to-indigo-600 text-white hover:from-sky-400 hover:to-indigo-500 shadow-sky-500/25'
            }`}
          >
            {loading ? (
              <>
                <RefreshCw className="h-4 w-4 animate-spin" />
                <span>Simulating...</span>
              </>
            ) : (
              <>
                <Play className="h-4 w-4 fill-current" />
                <span>Execute Simulation</span>
              </>
            )}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Architecture Selector */}
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Architecture Model
            </label>
            <select
              value={architecture}
              onChange={(e) => setArchitecture(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-sky-500"
            >
              <option value="hybrid_autoscaling">Hybrid Cloud (Autoscaling)</option>
              <option value="hybrid_fixed">Hybrid Cloud (Fixed 2 Instances)</option>
              <option value="on_premise">On-Premise (64 Fixed Cores)</option>
            </select>
          </div>

          {/* Workload Profile */}
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Workload Profile
            </label>
            <select
              value={selectedWorkload}
              onChange={(e) => setSelectedWorkload(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-sky-500"
            >
              <option value="W1">W1: Normal Steady-State (600 RPS)</option>
              <option value="W2">W2: Peak Business Hours (1400 RPS)</option>
              <option value="W3">W3: Extreme Stress (2600 RPS)</option>
              <option value="W4">W4: Promotional Burst (600→2800 RPS)</option>
              <option value="W5">W5: 50% Node Failure (1200 RPS)</option>
              <option value="W6">W6: Failure + DR Recovery (1200 RPS)</option>
            </select>
          </div>

          {/* Event Limit */}
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Event Batch Limit
            </label>
            <select
              value={maxEvents}
              onChange={(e) => setMaxEvents(Number(e.target.value))}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-sky-500"
            >
              <option value={500}>500 events (Fast preview)</option>
              <option value={1000}>1,000 events (Standard)</option>
              <option value={3000}>3,000 events (Deep trace)</option>
              <option value={5000}>5,000 events (Full workload)</option>
            </select>
          </div>

          {/* Seed */}
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              PRNG Seed (Academic Fairness)
            </label>
            <input
              type="number"
              value={seed}
              onChange={(e) => setSeed(Number(e.target.value))}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-sky-500"
            />
          </div>
        </div>
      </div>

      {/* Error display */}
      {error && (
        <div className="bg-rose-500/10 border border-rose-500/20 text-rose-400 p-4 rounded-xl flex items-center space-x-3">
          <AlertTriangle className="h-5 w-5 shrink-0" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      {/* Summary KPI Cards */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <span className="text-xs text-slate-400">Total Requests</span>
            <p className="text-xl font-bold text-white mt-1">{summary.total_requests.toLocaleString()}</p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <span className="text-xs text-slate-400">Avg Latency</span>
            <p className="text-xl font-bold text-sky-400 mt-1">{summary.avg_latency_ms.toFixed(2)} ms</p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <span className="text-xs text-slate-400">P95 Latency</span>
            <p className="text-xl font-bold text-indigo-400 mt-1">{summary.p95_latency_ms.toFixed(2)} ms</p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <span className="text-xs text-slate-400">Avg Queue Length</span>
            <p className="text-xl font-bold text-amber-400 mt-1">{summary.avg_queue_length.toFixed(1)}</p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <span className="text-xs text-slate-400">Avg Utilization</span>
            <p className="text-xl font-bold text-emerald-400 mt-1">{(summary.avg_utilization * 100).toFixed(1)}%</p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <span className="text-xs text-slate-400">Dropped Requests</span>
            <p className={`text-xl font-bold mt-1 ${summary.dropped_requests > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
              {summary.dropped_requests}
            </p>
          </div>
        </div>
      )}

      {/* Time Series Charts */}
      {timeSeries.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Latency & Queue Chart */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
            <h3 className="text-sm font-bold text-white mb-4 flex items-center space-x-2">
              <Activity className="h-4 w-4 text-sky-400" />
              <span>Response Time & Queue Length over Timeline</span>
            </h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={timeSeries}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="time_sec" stroke="#64748b" tick={{ fontSize: 11 }} />
                  <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }} />
                  <Legend />
                  <Line type="monotone" dataKey="latency_ms" name="Latency (ms)" stroke="#0ea5e9" dot={false} strokeWidth={2} />
                  <Line type="monotone" dataKey="queue_length" name="Queue Depth" stroke="#f59e0b" dot={false} strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Utilization & Active Instances Chart */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
            <h3 className="text-sm font-bold text-white mb-4 flex items-center space-x-2">
              <TrendingUp className="h-4 w-4 text-emerald-400" />
              <span>Server Utilization & Instance Scaling</span>
            </h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={timeSeries}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="time_sec" stroke="#64748b" tick={{ fontSize: 11 }} />
                  <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }} />
                  <Legend />
                  <Area type="monotone" dataKey="utilization" name="Utilization (%)" stroke="#10b981" fill="#10b981" fillOpacity={0.2} />
                  {timeSeries[0]?.active_instances !== undefined && (
                    <Area type="stepAfter" dataKey="active_instances" name="Active Public Instances" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.15} />
                  )}
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-12 text-center">
          <Activity className="h-10 w-10 text-slate-600 mx-auto mb-3 animate-pulse" />
          <h3 className="text-base font-semibold text-white mb-1">No Simulation Data Loaded</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            Select an architecture and workload profile above, then click <strong>Execute Simulation</strong> to trigger the SimPy discrete-event engine.
          </p>
        </div>
      )}

      {/* Scaling Events Log */}
      {scalingEvents.length > 0 && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
          <h3 className="text-sm font-bold text-white mb-3">Autoscaler Telemetry Events</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider font-semibold">
                <tr>
                  <th className="p-2.5">Sim Time (s)</th>
                  <th className="p-2.5">Event Type</th>
                  <th className="p-2.5">Instance Transition</th>
                  <th className="p-2.5">Autoscaler Trigger Reason</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 text-slate-300">
                {scalingEvents.map((evt, i) => (
                  <tr key={i} className="hover:bg-slate-800/40">
                    <td className="p-2.5 font-mono text-sky-400">{evt.timestamp.toFixed(2)}s</td>
                    <td className="p-2.5">
                      <span className={`px-2 py-0.5 rounded font-semibold text-[10px] ${
                        evt.event_type.includes('OUT') ? 'bg-purple-500/20 text-purple-300' : 'bg-blue-500/20 text-blue-300'
                      }`}>
                        {evt.event_type}
                      </span>
                    </td>
                    <td className="p-2.5 font-semibold text-white">
                      {evt.prev_instances} → {evt.new_instances} instances
                    </td>
                    <td className="p-2.5 text-slate-400">{evt.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
