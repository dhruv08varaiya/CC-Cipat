import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  Lock, 
  Key, 
  AlertOctagon, 
  Search, 
  CheckCircle, 
  XCircle,
  Cpu
} from 'lucide-react';
import { 
  fetchSecurityRules, 
  fetchRiskRegister, 
  classifyPayload 
} from '../api/client';

export const SecurityTab: React.FC = () => {
  const [rules, setRules] = useState<any>(null);
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
        return 'bg-rose-500/20 text-rose-300 border-rose-500/30';
      case 'CONFIDENTIAL':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/30';
      case 'INTERNAL':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
      default:
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30';
    }
  };

  return (
    <div className="space-y-6">
      {/* 4-Tier Zero Trust Classifier Sandbox */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
        <div className="flex items-center space-x-3 pb-4 border-b border-slate-800 mb-6">
          <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">4-Tier Zero-Trust Data Classifier Sandbox</h2>
            <p className="text-xs text-slate-400">Test live payload classification and compliance routing destination</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Input form */}
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                Banking Service Type
              </label>
              <select
                value={serviceType}
                onChange={(e) => setServiceType(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-sky-500"
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
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                Request Payload (JSON)
              </label>
              <textarea
                rows={5}
                value={payloadJson}
                onChange={(e) => setPayloadJson(e.target.value)}
                className="w-full bg-slate-950 font-mono text-xs border border-slate-700 rounded-lg p-3 text-slate-200 focus:outline-none focus:border-sky-500"
              />
            </div>

            <button
              onClick={handleTestClassify}
              disabled={classifying}
              className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-semibold text-sm hover:from-emerald-400 hover:to-teal-500 shadow-lg shadow-emerald-500/20 transition-all"
            >
              {classifying ? 'Analyzing Taint & Keywords...' : 'Classify Payload'}
            </button>

            {error && <p className="text-xs text-rose-400 mt-2">{error}</p>}
          </div>

          {/* Classification Output */}
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 flex flex-col justify-center">
            {classifyResult ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <span className="text-xs text-slate-400">Classified Tier</span>
                  <span className={`text-xs px-3 py-1 rounded-full font-bold border ${getBadgeClass(classifyResult.classification)}`}>
                    {classifyResult.classification}
                  </span>
                </div>
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <span className="text-xs text-slate-400">Target Datacenter Route</span>
                  <span className={`text-xs font-bold px-2 py-0.5 rounded ${
                    classifyResult.target_datacenter === 'PRIVATE' ? 'bg-indigo-500/20 text-indigo-300' : 'bg-sky-500/20 text-sky-300'
                  }`}>
                    {classifyResult.target_datacenter} CLOUD
                  </span>
                </div>
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <span className="text-xs text-slate-400">Processing Latency</span>
                  <span className="text-xs font-mono text-emerald-400">{classifyResult.processing_time_ms.toFixed(3)} ms</span>
                </div>
                <div>
                  <span className="text-xs text-slate-400 block mb-1">Decision Reason</span>
                  <p className="text-xs text-slate-300 bg-slate-900 p-2.5 rounded-lg border border-slate-800">
                    {classifyResult.decision_reason}
                  </p>
                </div>
                {classifyResult.tainted_fields?.length > 0 && (
                  <div>
                    <span className="text-xs text-slate-400 block mb-1">Tainted Sensitive Fields</span>
                    <div className="flex flex-wrap gap-1">
                      {classifyResult.tainted_fields.map((f: string, i: number) => (
                        <span key={i} className="text-[10px] bg-rose-500/10 text-rose-400 px-2 py-0.5 rounded border border-rose-500/20 font-mono">
                          {f}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8">
                <ShieldCheck className="h-10 w-10 text-slate-700 mx-auto mb-2" />
                <p className="text-xs text-slate-500">Run a payload classification test to view zero-trust routing decisions.</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Risk Register R1–R6 */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
        <h2 className="text-lg font-bold text-white mb-4 flex items-center space-x-2">
          <AlertOctagon className="h-5 w-5 text-amber-400" />
          <span>Security Risk Register (R1–R6)</span>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {riskRegister?.risks ? (
            Object.entries(riskRegister.risks).map(([key, risk]: [string, any]) => (
              <div key={key} className="bg-slate-950 border border-slate-800 rounded-xl p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono text-xs font-bold text-amber-400">{key}</span>
                  <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase ${
                    risk.severity === 'CRITICAL' ? 'bg-rose-500/20 text-rose-400' : 'bg-amber-500/20 text-amber-400'
                  }`}>
                    {risk.severity}
                  </span>
                </div>
                <h3 className="text-sm font-semibold text-white mb-1">{risk.title}</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-3">{risk.description}</p>
                <div className="border-t border-slate-800/80 pt-2 text-[11px] text-slate-500">
                  <span className="text-slate-400 font-medium">Mitigation: </span>
                  {risk.mitigation}
                </div>
              </div>
            ))
          ) : (
            <p className="text-xs text-slate-500">Loading risk register definitions...</p>
          )}
        </div>
      </div>
    </div>
  );
};
