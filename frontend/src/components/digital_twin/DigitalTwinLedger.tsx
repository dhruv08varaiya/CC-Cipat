import React from 'react';
import { ShieldCheck, Lock, AlertCircle, ArrowUpRight, CheckCircle2, XCircle } from 'lucide-react';
import { LiveTransaction } from '../../hooks/useDigitalTwinEngine';

interface LedgerProps {
  transactions: LiveTransaction[];
  totalProcessed: number;
  totalDropped: number;
}

export const DigitalTwinLedger: React.FC<LedgerProps> = ({ transactions, totalProcessed, totalDropped }) => {
  const getBadgeStyle = (tier: LiveTransaction['classification']) => {
    switch (tier) {
      case 'RESTRICTED':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
      case 'CONFIDENTIAL':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
      case 'INTERNAL':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
      case 'PUBLIC':
        return 'bg-slate-700/30 text-slate-300 border-slate-700/50';
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl">
      <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <ShieldCheck className="h-4 w-4 text-emerald-400" />
          <h4 className="text-xs font-bold text-white uppercase tracking-wider">
            Live Transaction Stream & Security Ledger
          </h4>
        </div>
        <div className="flex items-center space-x-3 text-[11px]">
          <span className="text-slate-400">Total Processed: <strong className="text-white font-mono">{totalProcessed.toLocaleString()}</strong></span>
          <span className="text-slate-400">Security Denials: <strong className="text-rose-400 font-mono">{totalDropped}</strong></span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider font-semibold text-[10px]">
            <tr>
              <th className="p-2">Time</th>
              <th className="p-2">Txn ID</th>
              <th className="p-2">Service Type</th>
              <th className="p-2">Security Tier</th>
              <th className="p-2">Cloud Target</th>
              <th className="p-2">Latency Breakdown</th>
              <th className="p-2 text-right">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
            {transactions.map((tx) => (
              <tr key={tx.id} className="hover:bg-slate-800/40 transition-colors">
                <td className="p-2 text-slate-400 text-[10px]">{tx.timestamp}</td>
                <td className="p-2 font-bold text-sky-400">{tx.id}</td>
                <td className="p-2 font-sans text-slate-200">
                  {tx.serviceType.replace(/_/g, ' ')}
                  {tx.amount && <span className="ml-1 text-[10px] text-emerald-400 font-mono font-bold">${tx.amount.toLocaleString()}</span>}
                </td>
                <td className="p-2">
                  <span className={`px-2 py-0.5 rounded text-[9px] font-bold border ${getBadgeStyle(tx.classification)}`}>
                    {tx.classification}
                  </span>
                </td>
                <td className="p-2">
                  <span className={`px-2 py-0.5 rounded text-[9px] font-bold ${
                    tx.targetTier === 'PRIVATE' ? 'bg-amber-500/15 text-amber-300' : 'bg-purple-500/15 text-purple-300'
                  }`}>
                    {tx.targetTier === 'PRIVATE' ? '🏢 ON-PREM DC' : '☁️ AWS CLOUD'}
                  </span>
                </td>
                <td className="p-2 text-[10px] text-slate-400">
                  <span title={`Net:${tx.breakdown.network}ms, Sec:${tx.breakdown.security}ms, Q:${tx.breakdown.queue}ms, Serv:${tx.breakdown.service}ms, DB:${tx.breakdown.db}ms`}>
                    {tx.latencyMs}ms <span className="text-slate-500">(Net:{tx.breakdown.network} + Serv:{tx.breakdown.service}{tx.breakdown.db > 0 ? ` + DB:${tx.breakdown.db}` : ''})</span>
                  </span>
                </td>
                <td className="p-2 text-right">
                  {tx.status === 'COMPLETED' && (
                    <span className="inline-flex items-center gap-1 text-emerald-400 font-bold text-[10px]">
                      <CheckCircle2 className="h-3 w-3" /> PASS
                    </span>
                  )}
                  {tx.status === 'BLOCKED' && (
                    <span className="inline-flex items-center gap-1 text-rose-400 font-bold text-[10px] animate-pulse">
                      <XCircle className="h-3 w-3" /> WAF BLOCK
                    </span>
                  )}
                  {tx.status === 'DROPPED' && (
                    <span className="inline-flex items-center gap-1 text-rose-400 font-bold text-[10px]">
                      <AlertCircle className="h-3 w-3" /> SATURATED
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
