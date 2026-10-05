import React from 'react';
import { LiveTransaction } from '../../hooks/useDigitalTwinEngine';

interface LedgerProps {
  transactions: LiveTransaction[];
}

export const DigitalTwinLedger: React.FC<LedgerProps> = ({ transactions }) => {
  const displayEvents = transactions.slice(0, 10);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
      case 'BLOCKED':
      case 'DROPPED':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
      default:
        return 'bg-sky-500/10 text-sky-400 border-sky-500/20';
    }
  };

  return (
    <div className="bg-[#12131A] border border-[#27272A] rounded-md p-3.5 space-y-2 h-full flex flex-col">
      <div className="flex items-center justify-between pb-1.5 border-b border-[#27272A]">
        <div className="flex items-center space-x-2">
          <span className="font-mono text-xs font-semibold text-zinc-200">
            TRANSACTION EVENT STREAM
          </span>
          <span className="font-mono text-[10px] text-zinc-500">&bull; Live Ring Buffer</span>
        </div>
        <span className="font-mono text-[10px] text-zinc-500">
          Last {displayEvents.length} events
        </span>
      </div>

      <div className="flex-1 overflow-x-auto">
        <table className="w-full text-left font-mono text-[11px]">
          <thead className="bg-[#090A0F] text-zinc-500 text-[10px] uppercase border-b border-[#27272A]">
            <tr>
              <th className="py-1 px-2 font-medium">Time</th>
              <th className="py-1 px-2 font-medium">TxID</th>
              <th className="py-1 px-2 font-medium">Service</th>
              <th className="py-1 px-2 font-medium">Route</th>
              <th className="py-1 px-2 font-medium text-right">Latency</th>
              <th className="py-1 px-2 font-medium text-center">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#27272A]/70">
            {displayEvents.map((tx) => (
              <tr key={tx.id} className="hover:bg-zinc-800/30 transition-colors">
                <td className="py-1.5 px-2 text-zinc-400 whitespace-nowrap">{tx.timestamp}</td>
                <td className="py-1.5 px-2 text-zinc-300 font-semibold">{tx.id}</td>
                <td className="py-1.5 px-2 text-zinc-300 truncate max-w-[130px]">{tx.serviceType}</td>
                <td className="py-1.5 px-2">
                  <span className={`text-[10px] px-1 py-0.2 rounded font-semibold ${
                    tx.targetTier === 'PRIVATE' ? 'text-indigo-400' : 'text-sky-400'
                  }`}>
                    {tx.targetTier}
                  </span>
                </td>
                <td className="py-1.5 px-2 text-right text-zinc-300">{tx.latencyMs.toFixed(1)}ms</td>
                <td className="py-1.5 px-2 text-center">
                  <span className={`px-1.5 py-0.2 rounded text-[9px] font-bold border ${getStatusBadge(tx.status)}`}>
                    {tx.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
