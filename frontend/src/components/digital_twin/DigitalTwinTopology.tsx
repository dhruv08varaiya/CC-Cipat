import React from 'react';
import { 
  Server, 
  Cloud, 
  ShieldCheck, 
  Database, 
  Cpu, 
  Zap, 
  Layers, 
  ArrowRight,
  AlertTriangle,
  Flame,
  CheckCircle2
} from 'lucide-react';
import { MetricSnapshot, DigitalTwinConfig } from '../../hooks/useDigitalTwinEngine';

interface TopologyProps {
  metrics: MetricSnapshot;
  config: DigitalTwinConfig;
}

export const DigitalTwinTopology: React.FC<TopologyProps> = ({ metrics, config }) => {
  const isPrivateStressed = metrics.privateUtilPct > 80;
  const isPublicStressed = metrics.publicUtilPct > 80;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-2xl relative overflow-hidden">
      {/* Background ambient grid */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b0a_1px,transparent_1px),linear-gradient(to_bottom,#1e293b0a_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none" />

      {/* Header */}
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800/80 relative z-10">
        <div className="flex items-center space-x-2.5">
          <div className="h-7 w-7 rounded-lg bg-sky-500/10 text-sky-400 border border-sky-500/20 flex items-center justify-center">
            <Layers className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white tracking-tight">Live Cluster Infrastructure Topology</h3>
            <p className="text-[11px] text-slate-400">Dynamic packet flow & multi-tier resource allocation</p>
          </div>
        </div>

        <div className="flex items-center space-x-2 text-xs">
          <span className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-mono text-[11px]">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-ping" />
            <span>60 FPS Live Sync</span>
          </span>
        </div>
      </div>

      {/* Topology Nodes Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-3 relative z-10 items-stretch">
        
        {/* Tier 1: Client Ingress Gateway (2 cols) */}
        <div className="lg:col-span-2 bg-slate-950/80 border border-slate-800 rounded-xl p-3.5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Ingress Gateway</span>
              <Zap className="h-3.5 w-3.5 text-amber-400 animate-pulse" />
            </div>
            <div className="bg-slate-900 border border-slate-800/80 rounded-lg p-2.5 text-center mb-2">
              <span className="text-[10px] text-slate-400 block">Traffic Inflow</span>
              <span className="text-base font-bold font-mono text-white">{metrics.rps.toLocaleString()}</span>
              <span className="text-[10px] text-slate-500 block">requests / sec</span>
            </div>
          </div>
          <div className="text-[10px] text-slate-400 space-y-1">
            <div className="flex justify-between">
              <span>Protocol:</span>
              <span className="font-mono text-sky-400">HTTP/2 TLS 1.3</span>
            </div>
            <div className="flex justify-between">
              <span>Drop Count:</span>
              <span className={`font-mono font-semibold ${metrics.droppedRequests > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                {metrics.droppedRequests}
              </span>
            </div>
          </div>
        </div>

        {/* Dynamic Connector 1 */}
        <div className="hidden lg:flex items-center justify-center text-slate-600">
          <ArrowRight className="h-4 w-4 animate-pulse text-sky-500" />
        </div>

        {/* Tier 2: 4-Tier Zero-Trust Security WAF (3 cols) */}
        <div className="lg:col-span-3 bg-slate-950/80 border border-slate-800 rounded-xl p-3.5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Zero-Trust WAF</span>
              <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
            </div>
            <div className="space-y-1.5 mb-2">
              <div className="flex items-center justify-between bg-slate-900 px-2 py-1 rounded text-[11px]">
                <span className="text-slate-400">PII / PCI-DSS Scan:</span>
                <span className="text-emerald-400 font-mono text-[10px] font-semibold flex items-center gap-1">
                  <CheckCircle2 className="h-2.5 w-2.5" /> 100% CLEAN
                </span>
              </div>
              <div className="flex items-center justify-between bg-slate-900 px-2 py-1 rounded text-[11px]">
                <span className="text-slate-400">AES-256 Envelope:</span>
                <span className="text-sky-400 font-mono text-[10px] font-semibold">1.2ms HSM Lat</span>
              </div>
              <div className="flex items-center justify-between bg-slate-900 px-2 py-1 rounded text-[11px]">
                <span className="text-slate-400">Classification:</span>
                <span className="text-purple-400 font-mono text-[10px] font-semibold">Deterministic</span>
              </div>
            </div>
          </div>
          {config.chaosAttackProbe ? (
            <div className="bg-rose-500/10 border border-rose-500/30 text-rose-400 px-2 py-1 rounded text-[10px] font-semibold text-center animate-pulse">
              ⚠️ MALICIOUS SQLi PROBE BLOCKED
            </div>
          ) : (
            <div className="text-[10px] text-slate-500 text-center font-mono">
              Enforcing NIST SP 800-207
            </div>
          )}
        </div>

        {/* Dynamic Connector 2 */}
        <div className="hidden lg:flex items-center justify-center text-slate-600">
          <ArrowRight className="h-4 w-4 animate-pulse text-indigo-500" />
        </div>

        {/* Tier 3: Dual-Tier Execution Clusters (5 cols: Split into Private DC & Public Cloud) */}
        <div className="lg:col-span-5 grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          
          {/* Node 3A: Private Secure Datacenter */}
          <div className={`bg-slate-950/80 border rounded-xl p-3 flex flex-col justify-between transition-all ${
            isPrivateStressed ? 'border-amber-500/50 shadow-lg shadow-amber-500/10' : 'border-slate-800'
          }`}>
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-[10px] font-bold text-amber-400 flex items-center gap-1">
                  <Server className="h-3 w-3" /> Private DC
                </span>
                {config.chaosCoreDrop ? (
                  <span className="text-[9px] px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-400 font-bold animate-pulse">
                    -50% CORES
                  </span>
                ) : (
                  <span className="text-[9px] font-mono text-slate-400">48 Cores</span>
                )}
              </div>

              {/* CPU Meter */}
              <div className="space-y-1 mb-2">
                <div className="flex justify-between text-[10px]">
                  <span className="text-slate-400">CPU Utilization</span>
                  <span className={`font-mono font-bold ${isPrivateStressed ? 'text-amber-400' : 'text-emerald-400'}`}>
                    {metrics.privateUtilPct}%
                  </span>
                </div>
                <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden">
                  <div 
                    className={`h-full transition-all duration-300 ${
                      metrics.privateUtilPct > 85 ? 'bg-rose-500' : metrics.privateUtilPct > 70 ? 'bg-amber-500' : 'bg-emerald-500'
                    }`}
                    style={{ width: `${metrics.privateUtilPct}%` }}
                  />
                </div>
              </div>

              {/* Queue Depth */}
              <div className="bg-slate-900 p-1.5 rounded text-[10px] flex justify-between items-center mb-1">
                <span className="text-slate-400">Queue Depth:</span>
                <span className={`font-mono font-bold ${metrics.privateQueue > 50 ? 'text-rose-400' : 'text-slate-200'}`}>
                  {metrics.privateQueue} reqs
                </span>
              </div>
            </div>

            <div className="flex items-center justify-between text-[9px] text-slate-500 border-t border-slate-900 pt-1 mt-1">
              <span>DB Pool:</span>
              <span className={`font-mono ${config.chaosDbLock ? 'text-rose-400 font-bold' : 'text-slate-300'}`}>
                {config.chaosDbLock ? '12/64 (LOCK)' : '24/64 Active'}
              </span>
            </div>
          </div>

          {/* Node 3B: Public Elastic Cloud */}
          <div className={`bg-slate-950/80 border rounded-xl p-3 flex flex-col justify-between transition-all ${
            isPublicStressed ? 'border-purple-500/50 shadow-lg shadow-purple-500/10' : 'border-slate-800'
          }`}>
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-[10px] font-bold text-sky-400 flex items-center gap-1">
                  <Cloud className="h-3 w-3" /> Public Cloud
                </span>
                <span className="text-[9px] px-1.5 py-0.5 rounded font-mono font-bold bg-purple-500/10 text-purple-300 border border-purple-500/20">
                  {metrics.activePublicInstances} Pods
                </span>
              </div>

              {/* CPU Meter */}
              <div className="space-y-1 mb-2">
                <div className="flex justify-between text-[10px]">
                  <span className="text-slate-400">Cluster Load</span>
                  <span className={`font-mono font-bold ${isPublicStressed ? 'text-purple-400' : 'text-sky-400'}`}>
                    {metrics.publicUtilPct}%
                  </span>
                </div>
                <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-sky-500 to-indigo-500 transition-all duration-300"
                    style={{ width: `${metrics.publicUtilPct}%` }}
                  />
                </div>
              </div>

              {/* Queue Depth */}
              <div className="bg-slate-900 p-1.5 rounded text-[10px] flex justify-between items-center mb-1">
                <span className="text-slate-400">Queue Depth:</span>
                <span className="font-mono font-bold text-slate-200">
                  {metrics.publicQueue} reqs
                </span>
              </div>
            </div>

            {/* Autoscaler Status Pill */}
            <div className="flex items-center justify-between text-[9px] border-t border-slate-900 pt-1 mt-1">
              <span className="text-slate-500">Autoscaler:</span>
              <span className={`font-mono font-bold px-1.5 py-0.2 rounded text-[9px] ${
                metrics.autoscalerState === 'SCALE_OUT' ? 'bg-amber-500/20 text-amber-300 animate-pulse' :
                metrics.autoscalerState === 'SCALE_IN' ? 'bg-blue-500/20 text-blue-300' :
                metrics.autoscalerState === 'COOLDOWN' ? 'bg-purple-500/20 text-purple-300' :
                'bg-emerald-500/10 text-emerald-400'
              }`}>
                {metrics.autoscalerState}
              </span>
            </div>
          </div>

        </div>

      </div>
    </div>
  );
};
