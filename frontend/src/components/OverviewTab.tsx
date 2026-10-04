import React from 'react';
import { 
  CheckCircle2, 
  Clock, 
  Cpu, 
  Cloud, 
  Shield, 
  BarChart3, 
  Database,
  ArrowRight,
  Zap
} from 'lucide-react';

export const OverviewTab: React.FC = () => {
  const stages = [
    { num: 1, name: 'Project Structure & Scaffolding', status: 'COMPLETE', date: 'Stage 1' },
    { num: 2, name: 'Synthetic Banking Dataset & Workloads (W1–W6)', status: 'COMPLETE', date: 'Stage 2' },
    { num: 3, name: 'On-Premise Baseline Discrete Simulation', status: 'COMPLETE', date: 'Stage 3' },
    { num: 4, name: 'Hybrid Cloud Simulation (Fixed Partitioning)', status: 'COMPLETE', date: 'Stage 4' },
    { num: 5, name: 'Load Balancing & Elastic Autoscaling (E4 Burst)', status: 'COMPLETE', date: 'Stage 5' },
    { num: 6, name: 'Security & 4-Tier Data Classification (E7 Benchmark)', status: 'COMPLETE', date: 'Stage 6' },
    { num: 7, name: 'Failure & Recovery Simulation (W5/W6 Chaos Injection)', status: 'PLANNED', date: 'Stage 7' },
    { num: 8, name: 'End-to-End Comparative Evaluation Suite (E1–E8)', status: 'PLANNED', date: 'Stage 8' },
    { num: 9, name: 'Comprehensive Graph & Metrics Suite', status: 'PLANNED', date: 'Stage 9' },
    { num: 10, name: 'Final Academic Report & Presentation Artifacts', status: 'PLANNED', date: 'Stage 10' },
  ];

  const layers = [
    {
      title: '1. Data Layer',
      icon: Database,
      color: 'from-amber-500/20 to-amber-600/5 text-amber-400 border-amber-500/20',
      description: '8 synthetic relational tables (170K rows) + 6 Poisson/bursty workload traces (W1–W6) in JSONL format.'
    },
    {
      title: '2. Simulation Engine',
      icon: Cpu,
      color: 'from-sky-500/20 to-sky-600/5 text-sky-400 border-sky-500/20',
      description: 'SimPy 4.1 discrete-event process engine with M/G/c queueing, finite FIFO buffers, and DB connection pooling.'
    },
    {
      title: '3. Infrastructure Models',
      icon: Cloud,
      color: 'from-blue-500/20 to-blue-600/5 text-blue-400 border-blue-500/20',
      description: 'On-Premise (64 fixed cores) vs. Hybrid Cloud (48 private cores + 2–20 elastic public instances) with Round-Robin LB.'
    },
    {
      title: '4. Security Layer',
      icon: Shield,
      color: 'from-emerald-500/20 to-emerald-600/5 text-emerald-400 border-emerald-500/20',
      description: '4-tier data classification (RESTRICTED to PUBLIC), Auth/MFA/RBAC simulation, AES-256 latency, and immutable audit logging.'
    },
    {
      title: '5. Experiment Layer',
      icon: Zap,
      color: 'from-purple-500/20 to-purple-600/5 text-purple-400 border-purple-500/20',
      description: 'Experiment runners for E1–E4 (load & burst autoscaling) and E7 (security compliance) with identical seed validation.'
    },
    {
      title: '6. Visualization Layer',
      icon: BarChart3,
      color: 'from-rose-500/20 to-rose-600/5 text-rose-400 border-rose-500/20',
      description: 'Modern React dashboard with interactive charts, time-series telemetry, and 16 publication figures.'
    },
  ];

  return (
    <div className="space-y-8">
      {/* Hero Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-slate-900/90 to-sky-950 border border-slate-800 p-8">
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/20 text-sky-400 text-xs font-semibold uppercase tracking-wider mb-4">
            <Zap className="h-3.5 w-3.5" />
            <span>Academic Capstone & Architecture Simulation</span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight sm:text-4xl mb-4">
            Secure Hybrid Cloud Banking Migration
          </h1>
          <p className="text-slate-300 text-base leading-relaxed mb-6">
            A discrete-event performance and security simulation framework modeling the migration of a tier-1 banking system from static on-premise infrastructure to an elastic hybrid cloud architecture.
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-3">
              <span className="text-xs text-slate-400">Simulation Engine</span>
              <p className="text-lg font-bold text-white">SimPy 4.1</p>
            </div>
            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-3">
              <span className="text-xs text-slate-400">Stages Complete</span>
              <p className="text-lg font-bold text-emerald-400">6 / 10</p>
            </div>
            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-3">
              <span className="text-xs text-slate-400">Synthetic Records</span>
              <p className="text-lg font-bold text-sky-400">170,000</p>
            </div>
            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-3">
              <span className="text-xs text-slate-400">Security Accuracy</span>
              <p className="text-lg font-bold text-purple-400">99.49%</p>
            </div>
          </div>
        </div>
      </div>

      {/* 6-Layer Architecture Grid */}
      <div>
        <h2 className="text-xl font-bold text-white mb-4 flex items-center space-x-2">
          <span>6-Layer Simulation Architecture</span>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {layers.map((layer, idx) => {
            const Icon = layer.icon;
            return (
              <div
                key={idx}
                className={`p-5 rounded-xl border bg-gradient-to-br ${layer.color} transition-all hover:scale-[1.01]`}
              >
                <div className="flex items-center space-x-3 mb-3">
                  <div className="p-2 rounded-lg bg-slate-900/80 border border-slate-700/50">
                    <Icon className="h-5 w-5" />
                  </div>
                  <h3 className="font-semibold text-white text-base">{layer.title}</h3>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">{layer.description}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* 10-Stage Roadmap Status */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
        <h2 className="text-xl font-bold text-white mb-4">10-Stage Development Roadmap</h2>
        <div className="space-y-3">
          {stages.map((stage) => {
            const isComplete = stage.status === 'COMPLETE';
            return (
              <div
                key={stage.num}
                className={`flex items-center justify-between p-3.5 rounded-xl border transition-all ${
                  isComplete
                    ? 'bg-slate-800/40 border-slate-700/60 hover:border-emerald-500/40'
                    : 'bg-slate-950/40 border-slate-800/80 opacity-70'
                }`}
              >
                <div className="flex items-center space-x-3">
                  {isComplete ? (
                    <CheckCircle2 className="h-5 w-5 text-emerald-400 shrink-0" />
                  ) : (
                    <Clock className="h-5 w-5 text-slate-500 shrink-0" />
                  )}
                  <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                    Stage {stage.num}
                  </span>
                  <span className={`text-sm font-medium ${isComplete ? 'text-white' : 'text-slate-400'}`}>
                    {stage.name}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span
                    className={`text-xs px-2.5 py-1 rounded-full font-semibold uppercase ${
                      isComplete
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                    }`}
                  >
                    {stage.status}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
