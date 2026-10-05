import React, { useState, useEffect } from 'react';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  Radio,
  FileCode,
  AlertTriangle
} from 'lucide-react';
import { traceTransaction, TraceTransactionResponse } from '../api/client';

export const LifecycleInspectorTab: React.FC = () => {
  const [selectedScenario, setSelectedScenario] = useState('wire_transfer');
  const [chaosNodeDrop, setChaosNodeDrop] = useState(false);
  const [chaosNetworkSpike, setChaosNetworkSpike] = useState(false);
  const [loading, setLoading] = useState(false);
  const [traceData, setTraceData] = useState<TraceTransactionResponse['trace'] | null>(null);
  
  // Playback state
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);

  const scenarios = [
    {
      id: 'wire_transfer',
      title: 'Wire Transfer ($15k)',
      service_type: 'fund_transfer',
      user_role: 'CUSTOMER',
      badge: 'RESTRICTED',
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
      badge: 'RESTRICTED',
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
      title: 'Balance Inquiry',
      service_type: 'balance_inquiry',
      user_role: 'CUSTOMER',
      badge: 'INTERNAL',
      badgeColor: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
      payload: {
        account_id: 'ACC_984128',
        channel: 'MOBILE_APP_IOS',
        session_id: 'sess_9941a8'
      }
    },
    {
      id: 'fx_rates',
      title: 'FX Currency Rates',
      service_type: 'fx_rates',
      user_role: 'CUSTOMER',
      badge: 'PUBLIC',
      badgeColor: 'bg-zinc-800 text-zinc-300 border-zinc-700',
      payload: {
        base_currency: 'USD',
        target_currencies: ['EUR', 'GBP', 'JPY', 'INR']
      }
    },
    {
      id: 'rbac_attack',
      title: 'Privilege Escalation Probe',
      service_type: 'fund_transfer',
      user_role: 'SECURITY_AUDITOR',
      badge: 'R2 ATTACK',
      badgeColor: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
      payload: {
        account_id: 'ACC_984128',
        recipient_id: 'ACC_999999',
        amount: 50000.00,
        unauthorized_override: true
      }
    },
    {
      id: 'chaos_drop',
      title: 'Node Outage Failover',
      service_type: 'fund_transfer',
      user_role: 'CUSTOMER',
      badge: 'FAILOVER',
      badgeColor: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
      payload: {
        account_id: 'ACC_984128',
        recipient_id: 'ACC_119482',
        amount: 250.00,
        force_failover_route: true
      }
    }
  ];

  const runTrace = async (scenId?: string) => {
    const targetId = scenId || selectedScenario;
    const scen = scenarios.find((s) => s.id === targetId) || scenarios[0];
    setLoading(true);
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
      setIsPlaying(false);
    } catch (e) {
      console.error('Trace execution failed', e);
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
      }, 1000 / playbackSpeed);
    } else if (isPlaying && traceData && currentStepIndex >= traceData.stages.length - 1) {
      setIsPlaying(false);
    }
    return () => clearTimeout(timer);
  }, [isPlaying, currentStepIndex, traceData, playbackSpeed]);

  const stages = traceData?.stages || [];
  const currentStage = stages[currentStepIndex] || null;

  return (
    <div className="space-y-3">
      {/* Top Toolbar */}
      <div className="bg-[#12131A] border border-[#27272A] rounded-md p-2.5 flex flex-wrap items-center justify-between gap-3 font-mono text-xs">
        <div className="flex items-center space-x-2">
          <span className="font-bold text-zinc-100">DISTRIBUTED TRACE INSPECTOR</span>
          <span className="text-[10px] text-zinc-500">&bull; 8-Stage Span Pipeline</span>
        </div>

        <div className="flex items-center space-x-4">
          <div>
            <span className="text-[10px] text-zinc-500">Transaction ID: </span>
            <span className="text-zinc-200 font-bold">{traceData?.transaction_id || 'TXN_984128'}</span>
          </div>
          <div>
            <span className="text-[10px] text-zinc-500">Total Latency: </span>
            <span className="text-emerald-400 font-bold">{traceData?.total_latency_ms.toFixed(2)} ms</span>
          </div>
        </div>
      </div>

      {/* Scenario Presets Bar */}
      <div className="bg-[#12131A] border border-[#27272A] rounded-md p-2.5 flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap gap-1.5 flex-1">
          {scenarios.map((scen) => {
            const isSelected = selectedScenario === scen.id;
            return (
              <button
                key={scen.id}
                onClick={() => {
                  setSelectedScenario(scen.id);
                  runTrace(scen.id);
                }}
                className={`px-2.5 py-1 rounded text-xs font-mono transition-colors flex items-center space-x-1.5 border ${
                  isSelected
                    ? 'bg-zinc-800 border-zinc-700 text-zinc-100 font-semibold'
                    : 'bg-[#090A0F] border-[#27272A] text-zinc-400 hover:text-zinc-200 hover:border-zinc-700'
                }`}
              >
                <span>{scen.title}</span>
                <span className={`text-[9px] px-1 py-0.2 rounded border ${scen.badgeColor}`}>
                  {scen.badge}
                </span>
              </button>
            );
          })}
        </div>

        {/* Stepper Controls */}
        <div className="flex items-center space-x-1.5 font-mono text-xs">
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="flex items-center space-x-1 px-2.5 py-1 rounded bg-zinc-800 text-zinc-200 hover:bg-zinc-700 transition-colors border border-zinc-700"
          >
            {isPlaying ? <Pause className="h-3 w-3 fill-current" /> : <Play className="h-3 w-3 fill-current" />}
            <span>{isPlaying ? 'Pause' : 'Play'}</span>
          </button>
          <button
            disabled={currentStepIndex <= 0}
            onClick={() => {
              setIsPlaying(false);
              setCurrentStepIndex((prev) => Math.max(0, prev - 1));
            }}
            className="px-2 py-1 rounded bg-[#090A0F] border border-[#27272A] text-zinc-300 disabled:opacity-30 hover:border-zinc-700"
          >
            Prev
          </button>
          <button
            disabled={!traceData || currentStepIndex >= traceData.stages.length - 1}
            onClick={() => {
              setIsPlaying(false);
              setCurrentStepIndex((prev) => Math.min((traceData?.stages.length || 1) - 1, prev + 1));
            }}
            className="px-2 py-1 rounded bg-zinc-800 text-zinc-100 border border-zinc-700 disabled:opacity-30 hover:bg-zinc-700 font-semibold"
          >
            Next
          </button>
        </div>
      </div>

      {/* Gantt Style Span Waterfall */}
      <div className="bg-[#12131A] border border-[#27272A] rounded-md p-3.5 space-y-3">
        <div className="flex items-center justify-between pb-1.5 border-b border-[#27272A]">
          <span className="font-mono text-xs font-semibold text-zinc-200">
            DISTRIBUTED TRACE WATERFALL
          </span>
          <span className="font-mono text-[10px] text-zinc-500">
            Click any span to inspect payload &amp; state
          </span>
        </div>

        <div className="space-y-1.5">
          {stages.map((stg, idx) => {
            const isCurrent = idx === currentStepIndex;
            const isCompleted = idx < currentStepIndex;
            const isBlocked = stg.status === 'BLOCKED';
            const totalMs = traceData?.total_latency_ms || 40;
            const leftPercent = (stg.timestamp_offset_ms / totalMs) * 100;
            const widthPercent = Math.max(5, (stg.duration_ms / totalMs) * 100);

            return (
              <div
                key={stg.stage_id}
                onClick={() => {
                  setIsPlaying(false);
                  setCurrentStepIndex(idx);
                }}
                className={`p-2 rounded border transition-colors cursor-pointer flex items-center justify-between font-mono text-xs ${
                  isCurrent
                    ? 'bg-zinc-800/80 border-zinc-600 text-white'
                    : isCompleted
                    ? 'bg-[#090A0F] border-[#27272A] text-zinc-300 hover:border-zinc-700'
                    : isBlocked
                    ? 'bg-rose-500/10 border-rose-500/30 text-rose-300'
                    : 'bg-[#090A0F] border-[#27272A] text-zinc-500'
                }`}
              >
                {/* Span Title */}
                <div className="w-56 shrink-0 flex items-center space-x-2 truncate">
                  <span className="text-[10px] px-1 py-0.2 rounded bg-zinc-800 text-zinc-400 font-bold">
                    S{stg.stage_id}
                  </span>
                  <span className="text-[11px] font-medium truncate">{stg.name}</span>
                </div>

                {/* Waterfall Gantt Span Bar */}
                <div className="flex-1 mx-3 h-4 bg-[#090A0F] border border-[#27272A] rounded relative overflow-hidden">
                  <div
                    className={`h-full rounded transition-all duration-300 ${
                      isBlocked ? 'bg-rose-500' : isCurrent ? 'bg-sky-400' : 'bg-emerald-500'
                    }`}
                    style={{
                      marginLeft: `${Math.min(90, Math.max(0, leftPercent))}%`,
                      width: `${Math.min(100 - leftPercent, widthPercent)}%`
                    }}
                  />
                </div>

                {/* Duration */}
                <div className="w-20 text-right shrink-0 text-[11px] text-zinc-400">
                  {stg.duration_ms.toFixed(2)} ms
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Stage Diagnostics & Live JSON */}
      {currentStage && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-3">
          {/* Stage Diagnostics (7 cols) */}
          <div className="lg:col-span-7 bg-[#12131A] border border-[#27272A] rounded-md p-3.5 space-y-2.5">
            <div className="flex items-center justify-between pb-1.5 border-b border-[#27272A]">
              <div className="flex items-center space-x-2">
                <span className="font-mono text-xs font-bold text-zinc-200">
                  STAGE {currentStage.stage_id}: {currentStage.name}
                </span>
              </div>
              <span className={`text-[10px] font-mono px-2 py-0.2 rounded font-bold border ${
                currentStage.status === 'SUCCESS' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                currentStage.status === 'BLOCKED' ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' :
                'bg-amber-500/10 text-amber-400 border-amber-500/20'
              }`}>
                {currentStage.status}
              </span>
            </div>

            <p className="text-xs font-mono text-zinc-300 leading-relaxed bg-[#090A0F] p-2.5 rounded border border-[#27272A]">
              {currentStage.description}
            </p>

            {/* Diagnostics Definition List */}
            <div>
              <span className="text-[10px] font-mono font-semibold text-zinc-500 uppercase tracking-wider block mb-1">
                Execution State
              </span>
              <dl className="grid grid-cols-2 gap-1.5 text-xs font-mono">
                {Object.entries(currentStage.details).map(([k, v]) => (
                  <div key={k} className="p-2 rounded bg-[#090A0F] border border-[#27272A] flex justify-between items-center">
                    <dt className="text-zinc-500 text-[10px]">{k}:</dt>
                    <dd className="text-zinc-200 text-[10px] font-medium truncate max-w-[140px]">
                      {String(v)}
                    </dd>
                  </div>
                ))}
              </dl>
            </div>
          </div>

          {/* Payload JSON (5 cols) */}
          <div className="lg:col-span-5 bg-[#12131A] border border-[#27272A] rounded-md p-3.5 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between pb-1.5 border-b border-[#27272A] mb-2">
                <div className="flex items-center space-x-1.5">
                  <FileCode className="h-3.5 w-3.5 text-zinc-400" />
                  <span className="text-xs font-mono font-bold text-zinc-200">PAYLOAD SNAPSHOT</span>
                </div>
                <span className="text-[9px] font-mono text-zinc-500">application/json</span>
              </div>
              <div className="bg-[#090A0F] p-2.5 rounded border border-[#27272A] font-mono text-[10px] text-zinc-300 max-h-[220px] overflow-y-auto">
                <pre className="whitespace-pre-wrap">{JSON.stringify(currentStage.payload_snapshot, null, 2)}</pre>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
