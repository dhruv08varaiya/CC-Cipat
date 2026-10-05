import React, { useState } from 'react';
import { 
  Play, 
  Pause, 
  Flame, 
  Globe, 
  Database, 
  ShieldAlert, 
  FileText,
  AlertTriangle,
  ChevronDown
} from 'lucide-react';
import { DigitalTwinConfig } from '../../hooks/useDigitalTwinEngine';

interface ControlsProps {
  config: DigitalTwinConfig;
  setConfig: React.Dispatch<React.SetStateAction<DigitalTwinConfig>>;
  applyPreset: (presetId: string) => void;
  onOpenSnapshot: () => void;
}

export const DigitalTwinControls: React.FC<ControlsProps> = ({
  config,
  setConfig,
  applyPreset,
  onOpenSnapshot,
}) => {
  const [chaosMenuOpen, setChaosMenuOpen] = useState(false);

  const isAnyChaosActive = config.chaosCoreDrop || config.chaosNetworkSpike || config.chaosDbLock || config.chaosAttackProbe;

  return (
    <div className="bg-[#12131A] border border-[#27272A] rounded-md p-2.5 flex flex-wrap items-center justify-between gap-3 text-xs">
      {/* Left: Scenario Presets */}
      <div className="flex items-center space-x-1 bg-[#090A0F] p-1 rounded border border-[#27272A]">
        {[
          { id: 'normal', label: 'Normal 600 RPS' },
          { id: 'salary_rush', label: 'Peak 1400 RPS' },
          { id: 'flash_burst', label: 'Flash Burst 2800 RPS' },
        ].map((preset) => {
          const isActive = config.preset === preset.id;
          return (
            <button
              key={preset.id}
              onClick={() => applyPreset(preset.id)}
              className={`px-2.5 py-1 rounded text-[11px] font-mono transition-colors ${
                isActive
                  ? 'bg-zinc-800 text-zinc-100 font-semibold border border-zinc-700'
                  : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              {preset.label}
            </button>
          );
        })}
      </div>

      {/* Center: Rate Scrubber */}
      <div className="flex items-center space-x-2.5 flex-1 max-w-sm">
        <span className="text-[11px] font-mono text-zinc-400 shrink-0">Rate</span>
        <input
          type="range"
          min={100}
          max={3000}
          step={50}
          value={config.targetRps}
          onChange={(e) => setConfig(prev => ({ ...prev, targetRps: Number(e.target.value), preset: 'custom' }))}
          className="w-full accent-zinc-200 h-1 bg-zinc-800 rounded cursor-pointer"
        />
        <span className="font-mono text-[11px] text-zinc-200 bg-[#090A0F] px-2 py-0.5 rounded border border-[#27272A] shrink-0">
          [{config.targetRps.toLocaleString()} RPS]
        </span>
      </div>

      {/* Right: Controls & Chaos Trigger */}
      <div className="flex items-center space-x-2">
        {/* Speed Multipliers */}
        <div className="flex bg-[#090A0F] p-0.5 rounded border border-[#27272A] text-[11px] font-mono">
          {[0.5, 1, 2].map((spd) => (
            <button
              key={spd}
              onClick={() => setConfig(prev => ({ ...prev, playbackSpeed: spd }))}
              className={`px-2 py-0.5 rounded transition-colors ${
                config.playbackSpeed === spd
                  ? 'bg-zinc-800 text-zinc-100 font-bold'
                  : 'text-zinc-500 hover:text-zinc-300'
              }`}
            >
              {spd}x
            </button>
          ))}
        </div>

        {/* Play/Pause */}
        <button
          onClick={() => setConfig(prev => ({ ...prev, isPaused: !prev.isPaused }))}
          className={`flex items-center space-x-1.5 px-2.5 py-1 rounded text-xs font-mono transition-colors border ${
            config.isPaused
              ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300'
              : 'bg-[#090A0F] border-[#27272A] text-zinc-300 hover:border-zinc-700'
          }`}
        >
          {config.isPaused ? <Play className="h-3 w-3 fill-current" /> : <Pause className="h-3 w-3 fill-current" />}
          <span>{config.isPaused ? 'Resume' : 'Pause'}</span>
        </button>

        {/* Chaos Injection Menu Dropdown */}
        <div className="relative">
          <button
            onClick={() => setChaosMenuOpen(!chaosMenuOpen)}
            className={`flex items-center space-x-1.5 px-2.5 py-1 rounded text-xs font-mono font-medium border transition-colors ${
              isAnyChaosActive
                ? 'bg-rose-500/20 border-rose-500/40 text-rose-300'
                : 'bg-[#090A0F] border-[#27272A] text-zinc-300 hover:border-zinc-700'
            }`}
          >
            <AlertTriangle className={`h-3 w-3 ${isAnyChaosActive ? 'text-rose-400' : 'text-zinc-400'}`} />
            <span>Chaos</span>
            <ChevronDown className="h-3 w-3 opacity-60" />
          </button>

          {chaosMenuOpen && (
            <div className="absolute right-0 mt-1 w-56 bg-[#12131A] border border-[#27272A] rounded-md shadow-xl p-2 z-50 space-y-1.5">
              <span className="text-[10px] font-mono text-zinc-400 block px-1 pb-1 border-b border-[#27272A]">
                Fault Injection Harness
              </span>
              
              <button
                onClick={() => setConfig(prev => ({ ...prev, chaosCoreDrop: !prev.chaosCoreDrop }))}
                className={`w-full flex items-center justify-between px-2 py-1.5 rounded text-[11px] font-mono transition-colors ${
                  config.chaosCoreDrop ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' : 'text-zinc-300 hover:bg-zinc-800'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <Flame className="h-3 w-3 text-rose-400" />
                  <span>50% Core Loss</span>
                </div>
                <span className="text-[10px]">{config.chaosCoreDrop ? 'ON' : 'OFF'}</span>
              </button>

              <button
                onClick={() => setConfig(prev => ({ ...prev, chaosNetworkSpike: !prev.chaosNetworkSpike }))}
                className={`w-full flex items-center justify-between px-2 py-1.5 rounded text-[11px] font-mono transition-colors ${
                  config.chaosNetworkSpike ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' : 'text-zinc-300 hover:bg-zinc-800'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <Globe className="h-3 w-3 text-amber-400" />
                  <span>+25ms Latency Lag</span>
                </div>
                <span className="text-[10px]">{config.chaosNetworkSpike ? 'ON' : 'OFF'}</span>
              </button>

              <button
                onClick={() => setConfig(prev => ({ ...prev, chaosDbLock: !prev.chaosDbLock }))}
                className={`w-full flex items-center justify-between px-2 py-1.5 rounded text-[11px] font-mono transition-colors ${
                  config.chaosDbLock ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30' : 'text-zinc-300 hover:bg-zinc-800'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <Database className="h-3 w-3 text-purple-400" />
                  <span>DB Pool Lock</span>
                </div>
                <span className="text-[10px]">{config.chaosDbLock ? 'ON' : 'OFF'}</span>
              </button>

              <button
                onClick={() => setConfig(prev => ({ ...prev, chaosAttackProbe: !prev.chaosAttackProbe }))}
                className={`w-full flex items-center justify-between px-2 py-1.5 rounded text-[11px] font-mono transition-colors ${
                  config.chaosAttackProbe ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'text-zinc-300 hover:bg-zinc-800'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <ShieldAlert className="h-3 w-3 text-emerald-400" />
                  <span>Attack Probe (R2)</span>
                </div>
                <span className="text-[10px]">{config.chaosAttackProbe ? 'ON' : 'OFF'}</span>
              </button>
            </div>
          )}
        </div>

        {/* Academic Snapshot */}
        <button
          onClick={onOpenSnapshot}
          className="flex items-center space-x-1.5 px-2.5 py-1 rounded text-xs font-mono bg-[#090A0F] border border-[#27272A] text-zinc-300 hover:border-zinc-700 transition-colors"
        >
          <FileText className="h-3 w-3 text-zinc-400" />
          <span>Snapshot</span>
        </button>
      </div>
    </div>
  );
};
