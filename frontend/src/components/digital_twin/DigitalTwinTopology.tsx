import React from 'react';
import { MetricSnapshot } from '../../hooks/useDigitalTwinEngine';

interface TopologyProps {
  metrics: MetricSnapshot;
  isPaused: boolean;
  isChaos: boolean;
}

export const DigitalTwinTopology: React.FC<TopologyProps> = ({
  metrics,
  isPaused,
  isChaos
}) => {
  const privateLoad = metrics.privateUtilPct || 32;
  const publicLoad = metrics.publicUtilPct || 65;
  const pods = metrics.activePublicInstances || 2;

  return (
    <div className="bg-[#12131A] border border-[#27272A] rounded-md p-3.5 space-y-3">
      <div className="flex items-center justify-between pb-2 border-b border-[#27272A]">
        <div className="flex items-center space-x-2">
          <span className="font-mono text-xs font-semibold text-zinc-200">
            SERVICE MESH TOPOLOGY &amp; ROUTING
          </span>
          <span className="font-mono text-[10px] text-zinc-500">
            &bull; NIST SP 800-207 Zero-Trust Architecture
          </span>
        </div>
        <div className="flex items-center space-x-2 font-mono text-[11px]">
          <span className="flex items-center space-x-1.5 text-zinc-400">
            <span className={`h-2 w-2 rounded-full ${isPaused ? 'bg-zinc-600' : 'bg-emerald-400 animate-pulse'}`} />
            <span>{isPaused ? 'PAUSED' : 'STREAMING 60Hz'}</span>
          </span>
          {isChaos && (
            <span className="px-1.5 py-0.2 rounded bg-rose-500/20 text-rose-300 text-[10px] border border-rose-500/30">
              FAULT INJECTED
            </span>
          )}
        </div>
      </div>

      {/* Interactive Topology Graph Area */}
      <div className="relative w-full overflow-x-auto">
        <div className="min-w-[860px] relative py-2">
          {/* SVG Vector Connections & Animated Particle Paths */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none z-0" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="curveGradPrivate" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#38BDF8" stopOpacity="0.8" />
                <stop offset="100%" stopColor="#10B981" stopOpacity="0.8" />
              </linearGradient>
              <linearGradient id="curveGradPublic" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#38BDF8" stopOpacity="0.8" />
                <stop offset="100%" stopColor="#818CF8" stopOpacity="0.8" />
              </linearGradient>
            </defs>

            {/* Path 1: Ingress -> Classifier */}
            <path
              d="M 160 85 L 220 85"
              stroke="#27272A"
              strokeWidth="2"
              fill="none"
            />
            {!isPaused && (
              <line
                x1="160" y1="85" x2="220" y2="85"
                stroke="#38BDF8"
                strokeWidth="2"
                strokeDasharray="4 6"
              />
            )}

            {/* Path 2: Classifier -> Load Balancer */}
            <path
              d="M 380 85 L 440 85"
              stroke="#27272A"
              strokeWidth="2"
              fill="none"
            />
            {!isPaused && (
              <line
                x1="380" y1="85" x2="440" y2="85"
                stroke="#10B981"
                strokeWidth="2"
                strokeDasharray="4 6"
              />
            )}

            {/* Path 3: Load Balancer -> Private DC (Curved Upper) */}
            <path
              d="M 600 75 C 640 75, 650 50, 690 50"
              stroke="url(#curveGradPrivate)"
              strokeWidth="2"
              fill="none"
              strokeDasharray={isPaused ? "none" : "4 4"}
            />

            {/* Path 4: Load Balancer -> Public Cloud (Curved Lower) */}
            <path
              d="M 600 95 C 640 95, 650 140, 690 140"
              stroke="url(#curveGradPublic)"
              strokeWidth="2"
              fill="none"
              strokeDasharray={isPaused ? "none" : "4 4"}
            />
          </svg>

          {/* Node Component Blocks */}
          <div className="grid grid-cols-12 gap-3 relative z-10 items-center">
            {/* 1. Ingress Gateway */}
            <div className="col-span-2 bg-[#090A0F] border border-[#27272A] rounded p-2.5 space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="font-mono text-[11px] font-bold text-zinc-200">Ingress</span>
                <span className="font-mono text-[9px] px-1 py-0.2 bg-zinc-800 text-zinc-400 rounded">TLS 1.3</span>
              </div>
              <div className="font-mono">
                <span className="text-[10px] text-zinc-500 block">Rate</span>
                <span className="text-base font-bold text-zinc-100">{metrics.rps.toLocaleString()}</span>
                <span className="text-[10px] text-zinc-500 ml-1">RPS</span>
              </div>
              <div className="text-[10px] font-mono text-zinc-500 flex justify-between border-t border-[#27272A] pt-1">
                <span>Drops</span>
                <span className="text-emerald-400">{metrics.droppedRequests}</span>
              </div>
            </div>

            {/* Edge label 1 */}
            <div className="col-span-1 text-center font-mono text-[10px] text-zinc-500">
              0.4ms
            </div>

            {/* 2. 4-Tier Security Classifier */}
            <div className="col-span-3 bg-[#090A0F] border border-[#27272A] rounded p-2.5 space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="font-mono text-[11px] font-bold text-zinc-200">Security Engine</span>
                <span className="font-mono text-[9px] px-1 py-0.2 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded">
                  4-Tier
                </span>
              </div>
              <div className="grid grid-cols-2 gap-1 font-mono text-[10px]">
                <div>
                  <span className="text-zinc-500 block">Taint</span>
                  <span className="text-emerald-400 font-semibold">Clean</span>
                </div>
                <div>
                  <span className="text-zinc-500 block">Cipher</span>
                  <span className="text-zinc-300">AES-256</span>
                </div>
              </div>
              <div className="text-[10px] font-mono text-zinc-500 flex justify-between border-t border-[#27272A] pt-1">
                <span>Inspection</span>
                <span className="text-zinc-300 font-semibold">0.38 ms</span>
              </div>
            </div>

            {/* Edge label 2 */}
            <div className="col-span-1 text-center font-mono text-[10px] text-zinc-500">
              0.4ms
            </div>

            {/* 3. Hybrid Load Balancer */}
            <div className="col-span-2 bg-[#090A0F] border border-[#27272A] rounded p-2.5 space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="font-mono text-[11px] font-bold text-zinc-200">Hybrid Router</span>
                <span className="font-mono text-[9px] px-1 py-0.2 bg-zinc-800 text-zinc-400 rounded">R-Robin</span>
              </div>
              <div className="font-mono">
                <span className="text-[10px] text-zinc-500 block">Split Ratio</span>
                <span className="text-xs font-semibold text-zinc-200">70% Priv / 30% Pub</span>
              </div>
              <div className="text-[10px] font-mono text-zinc-500 flex justify-between border-t border-[#27272A] pt-1">
                <span>Queue</span>
                <span className="text-zinc-300">{metrics.totalQueue} reqs</span>
              </div>
            </div>

            {/* Edge label 3 & 4 */}
            <div className="col-span-1 flex flex-col justify-between h-24 text-center font-mono text-[10px] text-zinc-500 py-1">
              <span>0.3ms</span>
              <span>14.2ms</span>
            </div>

            {/* 4. Target Clusters (Private DC & Public Cloud Stacked) */}
            <div className="col-span-2 space-y-2">
              {/* Private DC */}
              <div className="bg-[#090A0F] border border-[#27272A] rounded p-2 space-y-1">
                <div className="flex items-center justify-between font-mono text-[10px]">
                  <span className="font-bold text-zinc-200">Private DC</span>
                  <span className="text-zinc-500">48 Cores</span>
                </div>
                <div className="w-full bg-zinc-800 h-1.5 rounded overflow-hidden">
                  <div 
                    className="bg-emerald-500 h-full transition-all duration-300"
                    style={{ width: `${Math.min(100, privateLoad)}%` }}
                  />
                </div>
                <div className="flex justify-between font-mono text-[9px] text-zinc-500">
                  <span>Load: {privateLoad.toFixed(1)}%</span>
                  <span>Q: {metrics.privateQueue}</span>
                </div>
              </div>

              {/* Public Cloud */}
              <div className="bg-[#090A0F] border border-[#27272A] rounded p-2 space-y-1">
                <div className="flex items-center justify-between font-mono text-[10px]">
                  <span className="font-bold text-zinc-200">Public Cloud</span>
                  <span className="text-sky-400">{pods} Pods</span>
                </div>
                <div className="w-full bg-zinc-800 h-1.5 rounded overflow-hidden">
                  <div 
                    className="bg-sky-500 h-full transition-all duration-300"
                    style={{ width: `${Math.min(100, publicLoad)}%` }}
                  />
                </div>
                <div className="flex justify-between font-mono text-[9px] text-zinc-500">
                  <span>Load: {publicLoad.toFixed(1)}%</span>
                  <span>Q: {metrics.publicQueue}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
