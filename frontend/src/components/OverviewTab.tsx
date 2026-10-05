import React from 'react';
import { 
  CheckCircle2, 
  Cpu, 
  Cloud, 
  Shield, 
  BarChart3, 
  Database,
  Zap
} from 'lucide-react';

export const OverviewTab: React.FC = () => {
  const stages = [
    { num: 1, name: 'Project Structure & Scaffolding', status: 'COMPLETE' },
    { num: 2, name: 'Synthetic Banking Dataset & Workloads (W1–W6)', status: 'COMPLETE' },
    { num: 3, name: 'On-Premise Baseline Discrete Simulation', status: 'COMPLETE' },
    { num: 4, name: 'Hybrid Cloud Simulation (Fixed Partitioning)', status: 'COMPLETE' },
    { num: 5, name: 'Load Balancing & Elastic Autoscaling (E4 Burst)', status: 'COMPLETE' },
    { num: 6, name: 'Security & 4-Tier Data Classification (E7 Benchmark)', status: 'COMPLETE' },
    { num: 7, name: 'Failure & Recovery Simulation (W5/W6 Chaos Injection)', status: 'COMPLETE' },
    { num: 8, name: 'End-to-End Comparative Evaluation Suite (E1–E8)', status: 'COMPLETE' },
    { num: 9, name: 'Comprehensive Graph & Metrics Suite', status: 'COMPLETE' },
    { num: 10, name: 'Final Academic Report & Presentation Artifacts', status: 'COMPLETE' },
  ];

  const layers = [
    {
      title: '1. Data Layer',
      icon: Database,
      description: '8 relational tables (170k rows) and 6 Poisson/bursty workload traces (W1–W6) in JSONL format.'
    },
    {
      title: '2. Simulation Engine',
      icon: Cpu,
      description: 'SimPy 4.1 discrete-event process engine with M/G/c queueing, finite FIFO buffers, and DB connection pooling.'
    },
    {
      title: '3. Infrastructure Models',
      icon: Cloud,
      description: 'On-Premise (64 fixed cores) vs. Hybrid Cloud (48 private cores + 2–20 elastic public instances) with Round-Robin LB.'
    },
    {
      title: '4. Security Layer',
      icon: Shield,
      description: '4-tier data classification (RESTRICTED to PUBLIC), Auth/MFA/RBAC simulation, AES-256 latency, and audit logging.'
    },
    {
      title: '5. Experiment Layer',
      icon: Zap,
      description: 'Experiment runners for E1–E8 (load, burst autoscaling, fault tolerance, MTTR disaster recovery, TCO Pareto).'
    },
    {
      title: '6. Observability Layer',
      icon: BarChart3,
      description: 'React digital twin dashboard with interactive lifecycle inspector, rolling oscilloscopes, and publication exports.'
    },
  ];

  return (
    <div className="space-y-3 font-mono">
      {/* Overview Stat Header */}
      <div className="bg-[#12131A] border border-[#27272A] rounded-md p-3.5 space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-[#27272A]">
          <div>
            <h1 className="text-xs font-bold text-zinc-100 tracking-wide uppercase">
              Secure Hybrid Cloud Banking Migration Simulation
            </h1>
            <p className="text-[11px] text-zinc-500 mt-0.5">
              Discrete-event performance and security simulation framework modeling tier-1 banking migration
            </p>
          </div>
          <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            10 / 10 STAGES COMPLETE
          </span>
        </div>
        
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
          <div className="bg-[#090A0F] border border-[#27272A] rounded p-2">
            <span className="text-[10px] text-zinc-500">SIMULATION ENGINE</span>
            <p className="text-xs font-bold text-zinc-200 mt-0.5">SimPy 4.1.2</p>
          </div>
          <div className="bg-[#090A0F] border border-[#27272A] rounded p-2">
            <span className="text-[10px] text-zinc-500">SYNTHETIC DATASET</span>
            <p className="text-xs font-bold text-emerald-400 mt-0.5">170k Rows / 8 Tables</p>
          </div>
          <div className="bg-[#090A0F] border border-[#27272A] rounded p-2">
            <span className="text-[10px] text-zinc-500">BENCHMARK SUITE</span>
            <p className="text-xs font-bold text-sky-400 mt-0.5">E1 &ndash; E8 Complete</p>
          </div>
          <div className="bg-[#090A0F] border border-[#27272A] rounded p-2">
            <span className="text-[10px] text-zinc-500">3-YR TCO DELTA</span>
            <p className="text-xs font-bold text-purple-400 mt-0.5">-18.7% ($152k)</p>
          </div>
        </div>
      </div>

      {/* 6-Layer Architecture Grid */}
      <div className="bg-[#12131A] border border-[#27272A] rounded-md p-3.5 space-y-2.5">
        <h2 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">
          6-Layer Simulation Architecture
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2.5">
          {layers.map((layer, idx) => {
            const Icon = layer.icon;
            return (
              <div
                key={idx}
                className="p-3 rounded border border-[#27272A] bg-[#090A0F]"
              >
                <div className="flex items-center space-x-2 mb-1.5">
                  <div className="p-1 rounded bg-zinc-800 text-zinc-300">
                    <Icon className="h-3.5 w-3.5" />
                  </div>
                  <h3 className="font-semibold text-zinc-200 text-xs">{layer.title}</h3>
                </div>
                <p className="text-[11px] text-zinc-400 leading-relaxed">{layer.description}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* 10-Stage Roadmap Status */}
      <div className="bg-[#12131A] border border-[#27272A] rounded-md p-3.5 space-y-2.5">
        <h2 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">
          Development Stages (10 / 10)
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-1.5">
          {stages.map((stage) => (
            <div
              key={stage.num}
              className="flex items-center justify-between p-2 rounded border bg-[#090A0F] border-[#27272A] text-xs"
            >
              <div className="flex items-center space-x-2">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400 shrink-0" />
                <span className="text-[10px] text-zinc-500">
                  S{stage.num}
                </span>
                <span className="text-zinc-300 font-medium">
                  {stage.name}
                </span>
              </div>
              <span className="text-[9px] text-emerald-400 bg-emerald-500/10 px-1.5 py-0.2 rounded border border-emerald-500/20">
                COMPLETE
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
