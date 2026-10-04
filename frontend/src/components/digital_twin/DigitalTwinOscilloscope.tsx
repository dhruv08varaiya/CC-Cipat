import React from 'react';
import { Activity, Clock, Server, TrendingUp, AlertTriangle } from 'lucide-react';
import { MetricSnapshot } from '../../hooks/useDigitalTwinEngine';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  ReferenceLine
} from 'recharts';

interface OscilloscopeProps {
  history: MetricSnapshot[];
  currentMetrics: MetricSnapshot;
}

export const DigitalTwinOscilloscope: React.FC<OscilloscopeProps> = ({ history, currentMetrics }) => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      {/* 1. Response Time Waveform (Oscilloscope 1) */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl flex flex-col justify-between">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <Clock className="h-4 w-4 text-sky-400" />
            <h4 className="text-xs font-bold text-white uppercase tracking-wider">
              Latency Waveform & SLA Boundary
            </h4>
          </div>
          <div className="flex items-center space-x-3 text-xs">
            <span className="text-slate-400">Avg: <strong className="text-sky-400 font-mono">{currentMetrics.latencyMs}ms</strong></span>
            <span className="text-slate-400">P95: <strong className="text-indigo-400 font-mono">{currentMetrics.p95LatencyMs}ms</strong></span>
          </div>
        </div>

        <div className="h-48 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={history} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="2 2" stroke="#1e293b" />
              <XAxis dataKey="timeSec" stroke="#475569" tick={{ fontSize: 9 }} />
              <YAxis stroke="#475569" tick={{ fontSize: 9 }} domain={[0, 'dataMax + 20']} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#090d16', borderColor: '#334155', fontSize: '11px', borderRadius: '8px' }}
                labelFormatter={(label) => `Sim Time: ${label}s`}
              />
              <ReferenceLine y={45} stroke="#f43f5e" strokeDasharray="3 3" label={{ value: 'SLA Limit (45ms)', fill: '#f43f5e', fontSize: 10, position: 'insideTopRight' }} />
              <Line 
                type="monotone" 
                dataKey="latencyMs" 
                name="Avg Latency (ms)" 
                stroke="#0ea5e9" 
                dot={false} 
                strokeWidth={2}
                isAnimationActive={false}
              />
              <Line 
                type="monotone" 
                dataKey="p95LatencyMs" 
                name="P95 Latency (ms)" 
                stroke="#818cf8" 
                dot={false} 
                strokeWidth={1.5}
                strokeDasharray="2 2"
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="flex items-center justify-between text-[10px] text-slate-500 pt-2 border-t border-slate-800/60 mt-1">
          <span>Continuous Rolling Window: 30s</span>
          <span className="font-mono text-emerald-400">● Real-Time Feed</span>
        </div>
      </div>

      {/* 2. Cluster Utilization & Autoscaling Stream (Oscilloscope 2) */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl flex flex-col justify-between">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <TrendingUp className="h-4 w-4 text-emerald-400" />
            <h4 className="text-xs font-bold text-white uppercase tracking-wider">
              CPU Utilization & Autoscaling Pods
            </h4>
          </div>
          <div className="flex items-center space-x-3 text-xs">
            <span className="text-slate-400">Private: <strong className="text-amber-400 font-mono">{currentMetrics.privateUtilPct}%</strong></span>
            <span className="text-slate-400">Public: <strong className="text-purple-400 font-mono">{currentMetrics.publicUtilPct}%</strong></span>
          </div>
        </div>

        <div className="h-48 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={history} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="2 2" stroke="#1e293b" />
              <XAxis dataKey="timeSec" stroke="#475569" tick={{ fontSize: 9 }} />
              <YAxis stroke="#475569" tick={{ fontSize: 9 }} domain={[0, 100]} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#090d16', borderColor: '#334155', fontSize: '11px', borderRadius: '8px' }}
                labelFormatter={(label) => `Sim Time: ${label}s`}
              />
              <ReferenceLine y={70} stroke="#f59e0b" strokeDasharray="3 3" label={{ value: 'Scale Out (70%)', fill: '#f59e0b', fontSize: 10, position: 'insideTopLeft' }} />
              <Area 
                type="monotone" 
                dataKey="privateUtilPct" 
                name="Private DC CPU (%)" 
                stroke="#f59e0b" 
                fill="#f59e0b" 
                fillOpacity={0.15} 
                strokeWidth={1.5}
                isAnimationActive={false}
              />
              <Area 
                type="monotone" 
                dataKey="publicUtilPct" 
                name="Public Cloud CPU (%)" 
                stroke="#a855f7" 
                fill="#a855f7" 
                fillOpacity={0.2} 
                strokeWidth={2}
                isAnimationActive={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="flex items-center justify-between text-[10px] text-slate-500 pt-2 border-t border-slate-800/60 mt-1">
          <span>Active Elastic Pods: <strong className="text-purple-300 font-mono">{currentMetrics.activePublicInstances} instances</strong></span>
          <span className="font-mono text-purple-400">Scale Threshold: 70% / 35%</span>
        </div>
      </div>
    </div>
  );
};
