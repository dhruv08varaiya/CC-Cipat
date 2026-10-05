import React, { useState, useEffect } from 'react';
import { 
  Play, 
  RefreshCw, 
  Activity, 
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
  const [, setWorkloads] = useState<WorkloadItem[]>([]);
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
    <div className="space-y-3">
      {/* Control Panel */}
      <div className="bg-[#12131A] border border-[#27272A] rounded-md p-3.5 space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-[#27272A]">
          <div>
            <h2 className="text-xs font-mono font-bold text-zinc-100 uppercase tracking-wider">Simulation Runner</h2>
            <p className="text-[11px] font-mono text-zinc-500">SimPy discrete-event simulation engine with parameter modulation</p>
          </div>
          <button
            onClick={handleRunSimulation}
            disabled={loading}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded font-mono text-xs transition-colors ${
              loading
                ? 'bg-zinc-800 text-zinc-500 cursor-not-allowed'
                : 'bg-zinc-800 hover:bg-zinc-700 text-zinc-100 border border-zinc-700 font-semibold'
            }`}
          >
            {loading ? (
              <>
                <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                <span>Simulating...</span>
              </>
            ) : (
              <>
                <Play className="h-3.5 w-3.5 fill-current" />
                <span>Execute Simulation</span>
              </>
            )}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-2.5">
          {/* Architecture Selector */}
          <div>
            <label className="block text-[10px] font-mono font-semibold text-zinc-400 uppercase tracking-wider mb-1">
              Architecture Model
            </label>
            <select
              value={architecture}
              onChange={(e) => setArchitecture(e.target.value)}
              className="w-full bg-[#090A0F] border border-[#27272A] rounded px-2.5 py-1.5 text-xs text-zinc-200 focus:outline-none focus:border-zinc-500 font-mono"
            >
              <option value="hybrid_autoscaling">Hybrid Cloud (Autoscaling)</option>
              <option value="hybrid_fixed">Hybrid Cloud (Fixed 2 Instances)</option>
              <option value="on_premise">On-Premise (64 Cores)</option>
            </select>
          </div>

          {/* Workload Profile */}
          <div>
            <label className="block text-[10px] font-mono font-semibold text-zinc-400 uppercase tracking-wider mb-1">
              Workload Profile
            </label>
            <select
              value={selectedWorkload}
              onChange={(e) => setSelectedWorkload(e.target.value)}
              className="w-full bg-[#090A0F] border border-[#27272A] rounded px-2.5 py-1.5 text-xs text-zinc-200 focus:outline-none focus:border-zinc-500 font-mono"
            >
              <option value="W1">W1: Steady-State (600 RPS)</option>
              <option value="W2">W2: Peak Hours (1400 RPS)</option>
              <option value="W3">W3: Extreme Stress (2600 RPS)</option>
              <option value="W4">W4: Promotional Burst (2800 RPS)</option>
              <option value="W5">W5: 50% Node Loss (1200 RPS)</option>
              <option value="W6">W6: Failure + Recovery (1200 RPS)</option>
            </select>
          </div>

          {/* Event Limit */}
          <div>
            <label className="block text-[10px] font-mono font-semibold text-zinc-400 uppercase tracking-wider mb-1">
              Event Batch Limit
            </label>
            <select
              value={maxEvents}
              onChange={(e) => setMaxEvents(Number(e.target.value))}
              className="w-full bg-[#090A0F] border border-[#27272A] rounded px-2.5 py-1.5 text-xs text-zinc-200 focus:outline-none focus:border-zinc-500 font-mono"
            >
              <option value={500}>500 events</option>
              <option value={1000}>1,000 events</option>
              <option value={3000}>3,000 events</option>
              <option value={5000}>5,000 events</option>
            </select>
          </div>

          {/* Seed */}
          <div>
            <label className="block text-[10px] font-mono font-semibold text-zinc-400 uppercase tracking-wider mb-1">
              PRNG Seed
            </label>
            <input
              type="number"
              value={seed}
              onChange={(e) => setSeed(Number(e.target.value))}
              className="w-full bg-[#090A0F] border border-[#27272A] rounded px-2.5 py-1.5 text-xs text-zinc-200 focus:outline-none focus:border-zinc-500 font-mono"
            />
          </div>
        </div>
      </div>

      {/* Error display */}
      {error && (
        <div className="bg-rose-500/10 border border-rose-500/30 text-rose-400 p-3 rounded font-mono text-xs flex items-center space-x-2">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Summary KPI Cards */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-6 gap-2">
          <div className="bg-[#12131A] border border-[#27272A] rounded p-2.5">
            <span className="text-[10px] font-mono text-zinc-500 uppercase block">Total Requests</span>
            <p className="text-sm font-bold font-mono text-zinc-100 mt-0.5">{summary.total_requests.toLocaleString()}</p>
          </div>
          <div className="bg-[#12131A] border border-[#27272A] rounded p-2.5">
            <span className="text-[10px] font-mono text-zinc-500 uppercase block">Avg Latency</span>
            <p className="text-sm font-bold font-mono text-sky-400 mt-0.5">{summary.avg_latency_ms.toFixed(2)} ms</p>
          </div>
          <div className="bg-[#12131A] border border-[#27272A] rounded p-2.5">
            <span className="text-[10px] font-mono text-zinc-500 uppercase block">P95 Latency</span>
            <p className="text-sm font-bold font-mono text-indigo-400 mt-0.5">{summary.p95_latency_ms.toFixed(2)} ms</p>
          </div>
          <div className="bg-[#12131A] border border-[#27272A] rounded p-2.5">
            <span className="text-[10px] font-mono text-zinc-500 uppercase block">Avg Queue</span>
            <p className="text-sm font-bold font-mono text-amber-400 mt-0.5">{summary.avg_queue_length.toFixed(1)}</p>
          </div>
          <div className="bg-[#12131A] border border-[#27272A] rounded p-2.5">
            <span className="text-[10px] font-mono text-zinc-500 uppercase block">Utilization</span>
            <p className="text-sm font-bold font-mono text-zinc-200 mt-0.5">{(summary.avg_utilization * 100).toFixed(1)}%</p>
          </div>
          <div className="bg-[#12131A] border border-[#27272A] rounded p-2.5">
            <span className="text-[10px] font-mono text-zinc-500 uppercase block">Dropped</span>
            <p className={`text-sm font-bold font-mono mt-0.5 ${summary.dropped_requests > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
              {summary.dropped_requests}
            </p>
          </div>
        </div>
      )}

      {/* Time Series Charts */}
      {timeSeries.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
          {/* Latency & Queue Chart */}
          <div className="bg-[#12131A] border border-[#27272A] rounded-md p-3.5 space-y-2">
            <h3 className="text-xs font-mono font-bold text-zinc-200 uppercase tracking-wider flex items-center space-x-1.5">
              <Activity className="h-3.5 w-3.5 text-zinc-400" />
              <span>Latency &amp; Queue Length</span>
            </h3>
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={timeSeries} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="2 2" stroke="#27272A" />
                  <XAxis dataKey="time_sec" stroke="#52525B" tick={{ fontSize: 9, fontFamily: 'monospace' }} />
                  <YAxis stroke="#52525B" tick={{ fontSize: 9, fontFamily: 'monospace' }} />
                  <Tooltip contentStyle={{ backgroundColor: '#090A0F', borderColor: '#27272A', fontSize: '11px', fontFamily: 'monospace', color: '#F4F4F5' }} />
                  <Legend wrapperStyle={{ fontSize: '11px', fontFamily: 'monospace' }} />
                  <Line type="monotone" dataKey="latency_ms" name="Latency (ms)" stroke="#38BDF8" dot={false} strokeWidth={1.5} />
                  <Line type="monotone" dataKey="queue_length" name="Queue Depth" stroke="#F59E0B" dot={false} strokeWidth={1.5} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Utilization & Active Instances Chart */}
          <div className="bg-[#12131A] border border-[#27272A] rounded-md p-3.5 space-y-2">
            <h3 className="text-xs font-mono font-bold text-zinc-200 uppercase tracking-wider flex items-center space-x-1.5">
              <TrendingUp className="h-3.5 w-3.5 text-zinc-400" />
              <span>Utilization &amp; Scaling</span>
            </h3>
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={timeSeries} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="2 2" stroke="#27272A" />
                  <XAxis dataKey="time_sec" stroke="#52525B" tick={{ fontSize: 9, fontFamily: 'monospace' }} />
                  <YAxis stroke="#52525B" tick={{ fontSize: 9, fontFamily: 'monospace' }} />
                  <Tooltip contentStyle={{ backgroundColor: '#090A0F', borderColor: '#27272A', fontSize: '11px', fontFamily: 'monospace', color: '#F4F4F5' }} />
                  <Legend wrapperStyle={{ fontSize: '11px', fontFamily: 'monospace' }} />
                  <Area type="monotone" dataKey="utilization" name="Utilization (%)" stroke="#10B981" fill="#10B981" fillOpacity={0.12} />
                  {timeSeries[0]?.active_instances !== undefined && (
                    <Area type="stepAfter" dataKey="active_instances" name="Public Instances" stroke="#818CF8" fill="#818CF8" fillOpacity={0.15} />
                  )}
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-[#12131A] border border-[#27272A] rounded-md p-8 text-center font-mono">
          <Activity className="h-6 w-6 text-zinc-600 mx-auto mb-2" />
          <h3 className="text-xs font-semibold text-zinc-300 mb-0.5">No Simulation Telemetry</h3>
          <p className="text-[11px] text-zinc-500 max-w-sm mx-auto">
            Configure workload profile and click <strong>Execute Simulation</strong>.
          </p>
        </div>
      )}

      {/* Scaling Events Log */}
      {scalingEvents.length > 0 && (
        <div className="bg-[#12131A] border border-[#27272A] rounded-md p-3.5">
          <h3 className="text-xs font-mono font-bold text-zinc-200 uppercase tracking-wider mb-2">Autoscaler Event Log</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono text-xs">
              <thead className="bg-[#090A0F] text-zinc-500 uppercase text-[9px] border-b border-[#27272A]">
                <tr>
                  <th className="p-2">Time (s)</th>
                  <th className="p-2">Event</th>
                  <th className="p-2">Transition</th>
                  <th className="p-2">Reason</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#27272A] text-[11px] text-zinc-300">
                {scalingEvents.map((evt, i) => (
                  <tr key={i} className="hover:bg-zinc-800/30">
                    <td className="p-2 text-sky-400">{evt.timestamp.toFixed(2)}s</td>
                    <td className="p-2">
                      <span className={`px-1.5 py-0.2 rounded text-[9px] font-semibold ${
                        evt.event_type.includes('OUT') ? 'bg-purple-500/10 text-purple-300 border border-purple-500/20' : 'bg-blue-500/10 text-blue-300 border border-blue-500/20'
                      }`}>
                        {evt.event_type}
                      </span>
                    </td>
                    <td className="p-2 font-semibold text-zinc-100">
                      {evt.prev_instances} &rarr; {evt.new_instances}
                    </td>
                    <td className="p-2 text-zinc-400">{evt.reason}</td>
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
