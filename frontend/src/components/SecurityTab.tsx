import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  AlertOctagon
} from 'lucide-react';
import { 
  fetchSecurityRules, 
  fetchRiskRegister, 
  classifyPayload 
} from '../api/client';

export const SecurityTab: React.FC = () => {
  const [, setRules] = useState<any>(null);
  const [riskRegister, setRiskRegister] = useState<any>(null);
  const [serviceType, setServiceType] = useState('fund_transfer');
  const [payloadJson, setPayloadJson] = useState(
    JSON.stringify({ account_number: '1234567890', amount: 5000, recipient: 'Alice', ssn: '999-00-1234' }, null, 2)
  );
  const [classifyResult, setClassifyResult] = useState<any>(null);
  const [classifying, setClassifying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSecurityRules().then(setRules).catch(console.error);
    fetchRiskRegister().then(setRiskRegister).catch(console.error);
  }, []);

  const handleTestClassify = async () => {
    setClassifying(true);
    setError(null);
    try {
      const parsed = JSON.parse(payloadJson);
      const res = await classifyPayload(serviceType, parsed);
      setClassifyResult(res);
    } catch (err: any) {
      setError(err.message || 'Invalid JSON payload or classification error');
    } finally {
      setClassifying(false);
    }
  };

  const getBadgeClass = (tier: string) => {
    switch (tier) {
      case 'RESTRICTED':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
      case 'CONFIDENTIAL':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
      case 'INTERNAL':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
      default:
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
    }
  };

  return (
    <div className="space-y-3 font-mono">
      {/* 4-Tier Zero Trust Classifier Sandbox */}
      <div className="bg-[#12131A] border border-[#27272A] rounded-md p-3.5 space-y-3">
        <div className="flex items-center space-x-2.5 pb-2 border-b border-[#27272A]">
          <div className="p-1.5 rounded bg-zinc-800 text-zinc-300 border border-zinc-700">
            <ShieldCheck className="h-4 w-4" />
          </div>
          <div>
            <h2 className="text-xs font-bold text-zinc-100 uppercase tracking-wider">4-Tier Data Classifier Sandbox</h2>
            <p className="text-[11px] text-zinc-500">Deterministic taint analysis and destination routing verification</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
          {/* Input form */}
          <div className="space-y-2.5 bg-[#090A0F] border border-[#27272A] p-3 rounded">
            <div>
              <label className="block text-[10px] font-semibold text-zinc-400 uppercase tracking-wider mb-1">
                Banking Service Type
              </label>
              <select
                value={serviceType}
                onChange={(e) => setServiceType(e.target.value)}
                className="w-full bg-[#12131A] border border-[#27272A] rounded px-2.5 py-1.5 text-xs text-zinc-200 focus:outline-none focus:border-zinc-500"
              >
                <option value="fund_transfer">fund_transfer (RESTRICTED)</option>
                <option value="balance_inquiry">balance_inquiry (INTERNAL)</option>
                <option value="kyc_verification">kyc_verification (RESTRICTED)</option>
                <option value="transaction_history">transaction_history (CONFIDENTIAL)</option>
                <option value="fx_rates">fx_rates (PUBLIC)</option>
                <option value="atm_locator">atm_locator (PUBLIC)</option>
                <option value="account_statement">account_statement (CONFIDENTIAL)</option>
              </select>
            </div>

            <div>
              <label className="block text-[10px] font-semibold text-zinc-400 uppercase tracking-wider mb-1">
                Request Payload (JSON)
              </label>
              <textarea
                rows={5}
                value={payloadJson}
                onChange={(e) => setPayloadJson(e.target.value)}
                className="w-full bg-[#12131A] text-xs border border-[#27272A] rounded p-2 text-zinc-200 focus:outline-none focus:border-zinc-500"
              />
            </div>

            <button
              onClick={handleTestClassify}
              disabled={classifying}
              className="w-full py-1.5 px-3 rounded bg-zinc-800 border border-zinc-700 text-zinc-100 font-medium text-xs hover:bg-zinc-700 transition-colors disabled:opacity-50"
            >
              {classifying ? 'Analyzing Payload...' : 'Execute Classification'}
            </button>

            {error && <p className="text-xs text-rose-400 mt-1">{error}</p>}
          </div>

          {/* Classification Output */}
          <div className="bg-[#090A0F] border border-[#27272A] rounded p-3 flex flex-col justify-center text-xs">
            {classifyResult ? (
              <div className="space-y-2.5">
                <div className="flex items-center justify-between pb-2 border-b border-[#27272A]">
                  <span className="text-zinc-500">Classified Tier</span>
                  <span className={`text-xs px-2 py-0.5 rounded font-bold border ${getBadgeClass(classifyResult.classification)}`}>
                    {classifyResult.classification}
                  </span>
                </div>
                <div className="flex items-center justify-between pb-2 border-b border-[#27272A]">
                  <span className="text-zinc-500">Datacenter Route</span>
                  <span className={`text-xs font-bold px-2 py-0.5 rounded ${
                    classifyResult.target_datacenter === 'PRIVATE' ? 'bg-indigo-500/10 text-indigo-300 border border-indigo-500/20' : 'bg-sky-500/10 text-sky-300 border border-sky-500/20'
                  }`}>
                    {classifyResult.target_datacenter}
                  </span>
                </div>
                <div className="flex items-center justify-between pb-2 border-b border-[#27272A]">
                  <span className="text-zinc-500">Inspection Overhead</span>
                  <span className="text-emerald-400 font-bold">{classifyResult.processing_time_ms.toFixed(3)} ms</span>
                </div>
                <div>
                  <span className="text-zinc-500 block mb-1">Decision Reason</span>
                  <p className="text-zinc-300 bg-[#12131A] p-2 rounded border border-[#27272A]">
                    {classifyResult.decision_reason}
                  </p>
                </div>
                {classifyResult.tainted_fields?.length > 0 && (
                  <div>
                    <span className="text-zinc-500 block mb-1">Tainted Sensitive Fields</span>
                    <div className="flex flex-wrap gap-1">
                      {classifyResult.tainted_fields.map((f: string, i: number) => (
                        <span key={i} className="text-[10px] bg-rose-500/10 text-rose-400 px-1.5 py-0.2 rounded border border-rose-500/20">
                          {f}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-6">
                <ShieldCheck className="h-6 w-6 text-zinc-700 mx-auto mb-1.5" />
                <p className="text-[11px] text-zinc-500">Run a payload classification test to inspect zero-trust routing decisions.</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Risk Register R1–R6 */}
      <div className="bg-[#12131A] border border-[#27272A] rounded-md p-3.5">
        <div className="flex items-center space-x-2 pb-2 border-b border-[#27272A] mb-2.5">
          <AlertOctagon className="h-4 w-4 text-amber-400" />
          <h2 className="text-xs font-bold text-zinc-100 uppercase">Security Risk Register (R1–R6)</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2.5">
          {riskRegister?.risks ? (
            Object.entries(riskRegister.risks).map(([key, risk]: [string, any]) => (
              <div key={key} className="bg-[#090A0F] border border-[#27272A] rounded p-2.5">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-bold text-amber-400">{key}</span>
                  <span className={`text-[9px] px-1.5 py-0.2 rounded font-bold uppercase ${
                    risk.severity === 'CRITICAL' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                  }`}>
                    {risk.severity}
                  </span>
                </div>
                <h3 className="text-xs font-semibold text-zinc-200 mb-1">{risk.title}</h3>
                <p className="text-[11px] text-zinc-400 leading-relaxed mb-2">{risk.description}</p>
                <div className="border-t border-[#27272A] pt-1.5 text-[10px] text-zinc-500">
                  <span className="text-zinc-400 font-medium">Mitigation: </span>
                  {risk.mitigation}
                </div>
              </div>
            ))
          ) : (
            <p className="text-xs text-zinc-500">Loading risk register definitions...</p>
          )}
        </div>
      </div>
    </div>
  );
};
