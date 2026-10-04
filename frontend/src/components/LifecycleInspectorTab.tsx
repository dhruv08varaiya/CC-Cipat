import React, { useState, useEffect } from 'react';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  ChevronRight, 
  ShieldCheck, 
  Lock, 
  Cpu, 
  Server, 
  Database, 
  Clock, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle,
  Zap,
  ArrowRight,
  Fingerprint,
  Radio,
  FileCode
} from 'lucide-react';
import { traceTransaction, LifecycleStageItem, TraceTransactionResponse } from '../api/client';

export const LifecycleInspectorTab: React.FC = () => {
  const [selectedScenario, setSelectedScenario] = useState('wire_transfer');
  const [chaosNodeDrop, setChaosNodeDrop] = useState(false);
  const [chaosNetworkSpike, setChaosNetworkSpike] = useState(false);
  const [loading, setLoading] = useState(false);
  const [traceData, setTraceData] = useState<TraceTransactionResponse['trace'] | null>(null);
  
  // Playback state
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1); // 1x = 1000ms per step

  const scenarios = [
    {
      id: 'wire_transfer',
      title: 'High-Value Wire Transfer ($15,000)',
      service_type: 'fund_transfer',
      user_role: 'CUSTOMER',
      badge: 'RESTRICTED / MFA',
      badgeColor: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
      payload: {
        account_id: 'ACC_984128',
        recipient_id: 'ACC_119482',
        amount: 15000.00,
        currency: 'USD',
        ssn_last4: '8841',
        auth_token: 'tok_sec_9941a8',
        device_fingerprint: 'dev_mac_x8812'
      }
    },
    {
      id: 'kyc_upload',
      title: 'KYC Document Verification',
      service_type: 'kyc_verification',
      user_role: 'BANK_OPERATOR',
      badge: 'RESTRICTED / PRIVATE',
      badgeColor: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
      payload: {
        customer_id: 'CUST_55102',
        document_type: 'PASSPORT',
        document_hash: 'sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
        verified_by: 'OPERATOR_44'
      }
    },
    {
      id: 'balance_inquiry',
      title: 'Mobile Balance Inquiry',
      service_type: 'balance_inquiry',
      user_role: 'CUSTOMER',
      badge: 'INTERNAL / PUBLIC CLOUD',
      badgeColor: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
      payload: {
        account_id: 'ACC_984128',
        channel: 'MOBILE_APP_IOS',
        session_id: 'sess_9941a8'
      }
    },
    {
      id: 'fx_rates',
      title: 'Live FX Currency Rates',
      service_type: 'fx_rates',
      user_role: 'CUSTOMER',
      badge: 'PUBLIC / EDGE CACHED',
      badgeColor: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
      payload: {
        base_currency: 'USD',
        target_currencies: ['EUR', 'GBP', 'JPY', 'INR']
      }
    },
    {
      id: 'rbac_attack',
      title: 'Privilege Escalation Attack Probe',
      service_type: 'fund_transfer',
      user_role: 'SECURITY_AUDITOR', // Auditors cannot transfer funds
      badge: 'BLOCKED / R2 VIOLATION',
      badgeColor: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
      payload: {
        account_id: 'ACC_SYS_001',
        recipient_id: 'ACC_ATTACK_99',
        amount: 500000.00,
        tampered_role: 'ADMIN'
      }
    }
  ];

  const runTrace = async (scenarioId = selectedScenario) => {
    setLoading(true);
    setIsPlaying(false);
    const scen = scenarios.find((s) => s.id === scenarioId) || scenarios[0];
    try {
      const res = await traceTransaction({
        service_type: scen.service_type,
        user_role: scen.user_role,
        payload: scen.payload,
        chaos_node_failure: chaosNodeDrop,
        chaos_network_spike: chaosNetworkSpike
      });
      setTraceData(res.trace);
      setCurrentStepIndex(0);
      setIsPlaying(true);
    } catch (err) {
      console.error('Failed to run lifecycle trace:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runTrace('wire_transfer');
  }, [chaosNodeDrop, chaosNetworkSpike]);

  // Playback timer
  useEffect(() => {
    let timer: any;
    if (isPlaying && traceData && currentStepIndex < traceData.stages.length - 1) {
      timer = setTimeout(() => {
        setCurrentStepIndex((prev) => prev + 1);
      }, 1200 / playbackSpeed);
    } else if (isPlaying && traceData && currentStepIndex >= traceData.stages.length - 1) {
      setIsPlaying(false);
    }
    return () => clearTimeout(timer);
  }, [isPlaying, currentStepIndex, traceData, playbackSpeed]);

  const stages = traceData?.stages || [];
  const currentStage = stages[currentStepIndex] || null;

  const stageIcons = [
    Radio,
    ShieldCheck,
    Fingerprint,
    ArrowRight,
    Server,
    Cpu,
    Lock,
    CheckCircle2
  ];

  return (
    <div className="space-y-6">
      {/* Top Header & Hardware Efficiency Badge */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-2xl">
        <div>
          <div className="flex items-center space-x-2">
            <div className="h-8 w-8 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center justify-center">
              <Zap className="h-4 w-4" />
            </div>
            <h1 className="text-xl font-bold text-white">Glass-Box System Lifecycle Inspector</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Real-time step-by-step visual trace through all 8 banking simulation layers
          </p>
        </div>


      </div>

      {/* Scenario Presets & Chaos Triggers */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Scenarios (2 cols) */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 p-4 rounded-2xl">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-3">
            1. Select Action Scenario
          </span>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {scenarios.map((scen) => {
              const isSelected = selectedScenario === scen.id;
              return (
                <button
                  key={scen.id}
                  onClick={() => {
                    setSelectedScenario(scen.id);
                    runTrace(scen.id);
                  }}
                  className={`p-3 rounded-xl border text-left transition-all flex flex-col justify-between ${
                    isSelected
                      ? 'bg-sky-500/10 border-sky-500 text-white shadow-md shadow-sky-500/10'
                      : 'bg-slate-950 border-slate-800/80 text-slate-400 hover:text-slate-200 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-bold text-white">{scen.title}</span>
                  </div>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded border inline-block w-fit ${scen.badgeColor}`}>
                    {scen.badge}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Chaos Injection Toggles (1 col) */}
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-2xl flex flex-col justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-3 flex items-center space-x-1.5">
              <AlertTriangle className="h-3.5 w-3.5 text-amber-400" />
              <span>2. Chaos Injection Lab</span>
            </span>
            <div className="space-y-2.5">
              <label className="flex items-center space-x-3 p-2.5 rounded-xl bg-slate-950 border border-slate-800 cursor-pointer hover:border-slate-700">
                <input
                  type="checkbox"
                  checked={chaosNodeDrop}
                  onChange={(e) => setChaosNodeDrop(e.target.checked)}
                  className="rounded bg-slate-900 border-slate-700 text-sky-500 focus:ring-0"
                />
                <div>
                  <span className="text-xs font-semibold text-white block">Simulate 50% Node Outage</span>
                  <span className="text-[10px] text-slate-400 block">Triggers M/G/c queue backpressure</span>
                </div>
              </label>

              <label className="flex items-center space-x-3 p-2.5 rounded-xl bg-slate-950 border border-slate-800 cursor-pointer hover:border-slate-700">
                <input
                  type="checkbox"
                  checked={chaosNetworkSpike}
                  onChange={(e) => setChaosNetworkSpike(e.target.checked)}
                  className="rounded bg-slate-900 border-slate-700 text-sky-500 focus:ring-0"
                />
                <div>
                  <span className="text-xs font-semibold text-white block">Inject 4.5x WAN Latency Spike</span>
                  <span className="text-[10px] text-slate-400 block">Degrades public cloud transit</span>
                </div>
              </label>
            </div>
          </div>

          <button
            onClick={() => runTrace()}
            disabled={loading}
            className="w-full mt-3 py-2 px-3 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 text-white text-xs font-bold hover:from-sky-400 hover:to-indigo-500 transition-all flex items-center justify-center space-x-1.5 shadow-md shadow-sky-500/20"
          >
            <RotateCcw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Re-Execute Action Trace</span>
          </button>
        </div>
      </div>

      {/* Interactive 8-Stage Stepper Track */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <div className="flex items-center justify-between pb-4 mb-6 border-b border-slate-800">
          <div className="flex items-center space-x-3">
            <span className="text-xs font-bold font-mono px-2.5 py-1 rounded-lg bg-sky-500/20 text-sky-300 border border-sky-500/30">
              TXN: {traceData?.transaction_id || 'TXN_984128'}
            </span>
            <span className="text-xs text-slate-400">
              Total Latency: <strong className="text-emerald-400 font-mono">{traceData?.total_latency_ms.toFixed(2)} ms</strong>
            </span>
          </div>

          {/* Stepper Controls */}
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 text-white text-xs font-semibold hover:bg-slate-700"
            >
              {isPlaying ? <Pause className="h-3.5 w-3.5" /> : <Play className="h-3.5 w-3.5 fill-current" />}
              <span>{isPlaying ? 'Pause' : 'Auto Play'}</span>
            </button>
            <button
              disabled={currentStepIndex <= 0}
              onClick={() => {
                setIsPlaying(false);
                setCurrentStepIndex((prev) => Math.max(0, prev - 1));
              }}
              className="px-2.5 py-1.5 rounded-lg bg-slate-800 text-slate-300 text-xs font-semibold disabled:opacity-40 hover:bg-slate-700"
            >
              Prev
            </button>
            <button
              disabled={!traceData || currentStepIndex >= traceData.stages.length - 1}
              onClick={() => {
                setIsPlaying(false);
                setCurrentStepIndex((prev) => Math.min((traceData?.stages.length || 1) - 1, prev + 1));
              }}
              className="px-2.5 py-1.5 rounded-lg bg-sky-600 text-white text-xs font-semibold disabled:opacity-40 hover:bg-sky-500"
            >
              Next
            </button>
            <select
              value={playbackSpeed}
              onChange={(e) => setPlaybackSpeed(Number(e.target.value))}
              className="bg-slate-950 border border-slate-700 text-xs text-slate-300 rounded-lg px-2 py-1 focus:outline-none"
            >
              <option value={0.5}>0.5x Speed</option>
              <option value={1}>1.0x Speed</option>
              <option value={2}>2.0x Speed</option>
            </select>
          </div>
        </div>

        {/* 8-Stage Visual Nodes Flow */}
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2">
          {stages.map((stg, idx) => {
            const Icon = stageIcons[idx] || Radio;
            const isCurrent = idx === currentStepIndex;
            const isCompleted = idx < currentStepIndex;
            const isBlocked = stg.status === 'BLOCKED';
            const isWarning = stg.status === 'WARNING';

            let nodeBg = 'bg-slate-950 border-slate-800 text-slate-500';
            if (isCurrent) {
              nodeBg = 'bg-sky-500/20 border-sky-400 text-sky-300 shadow-lg shadow-sky-500/20 ring-2 ring-sky-500/40';
            } else if (isCompleted) {
              nodeBg = 'bg-emerald-500/10 border-emerald-500/40 text-emerald-400';
            } else if (isBlocked) {
              nodeBg = 'bg-rose-500/20 border-rose-500 text-rose-300';
            }

            return (
              <button
                key={stg.stage_id}
                onClick={() => {
                  setIsPlaying(false);
                  setCurrentStepIndex(idx);
                }}
                className={`p-3 rounded-xl border text-center transition-all relative flex flex-col items-center justify-between min-h-[110px] ${nodeBg}`}
              >
                <div className="flex items-center justify-between w-full text-[10px] font-mono">
                  <span>#{stg.stage_id}</span>
                  <span>{stg.duration_ms.toFixed(1)}ms</span>
                </div>
                <div className="my-1.5 p-2 rounded-lg bg-slate-900/80">
                  <Icon className="h-4 w-4" />
                </div>
                <span className="text-[11px] font-semibold leading-tight line-clamp-2">
                  {stg.name}
                </span>
                {isCurrent && (
                  <span className="absolute -top-1 -right-1 flex h-2.5 w-2.5">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-sky-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-sky-500"></span>
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Detailed Stage Inspector & Live Data Mutation Box */}
      {currentStage && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Stage Diagnostics (Col 1 & 2) */}
          <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center space-x-2">
                <span className="h-6 w-6 rounded-full bg-sky-500/20 text-sky-400 flex items-center justify-center font-bold text-xs">
                  {currentStage.stage_id}
                </span>
                <h3 className="text-base font-bold text-white">{currentStage.name}</h3>
              </div>
              <span className={`text-xs px-2.5 py-0.5 rounded-full font-bold border ${
                currentStage.status === 'SUCCESS' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                currentStage.status === 'BLOCKED' ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' :
                'bg-amber-500/10 text-amber-400 border-amber-500/20'
              }`}>
                {currentStage.status}
              </span>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed bg-slate-950 p-3 rounded-xl border border-slate-800/80">
              {currentStage.description}
            </p>

            {/* Key-Value Diagnostics Table */}
            <div>
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
                Stage Diagnostic Telemetry
              </span>
              <div className="grid grid-cols-2 gap-2 text-xs">
                {Object.entries(currentStage.details).map(([k, v]) => (
                  <div key={k} className="p-2.5 rounded-lg bg-slate-950 border border-slate-800/60 flex justify-between items-center">
                    <span className="text-slate-400 font-mono text-[11px]">{k}</span>
                    <span className="text-white font-semibold font-mono text-[11px] truncate max-w-[140px]">
                      {String(v)}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Latency Contribution */}
            <div className="pt-2">
              <div className="flex justify-between text-xs text-slate-400 mb-1">
                <span>Stage Latency Contribution</span>
                <span className="font-mono text-emerald-400 font-bold">
                  {currentStage.duration_ms.toFixed(2)} ms (accumulated: {currentStage.timestamp_offset_ms.toFixed(2)} ms)
                </span>
              </div>
              <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
                <div
                  className="h-full bg-gradient-to-r from-sky-500 to-indigo-500 rounded-full"
                  style={{
                    width: `${Math.min(100, Math.max(10, (currentStage.duration_ms / (traceData?.total_latency_ms || 1)) * 100))}%`
                  }}
                ></div>
              </div>
            </div>
          </div>

          {/* Live Payload Mutation Box (Col 3) */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-3">
                <div className="flex items-center space-x-2">
                  <FileCode className="h-4 w-4 text-sky-400" />
                  <span className="text-xs font-bold text-white">Live Payload State</span>
                </div>
                <span className="text-[10px] font-mono text-slate-500">JSON In-Memory</span>
              </div>
              <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 font-mono text-[11px] text-slate-300 max-h-[300px] overflow-y-auto">
                <pre>{JSON.stringify(currentStage.payload_snapshot, null, 2)}</pre>
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-400">
              <p>
                Watch how the payload mutates at <strong>Stage 2</strong> (Classification tags) and scrambles at <strong>Stage 7</strong> (AES-256 ciphertext).
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
