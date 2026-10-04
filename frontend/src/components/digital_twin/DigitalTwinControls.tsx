import React from 'react';
import { 
  Play, 
  Pause, 
  Flame, 
  AlertTriangle, 
  Globe, 
  Database, 
  ShieldAlert, 
  RotateCcw, 
  FileText,
  Sliders,
  Zap,
  Sparkles
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
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-2xl space-y-4">
      {/* Top Action Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <Sliders className="h-4 w-4 text-sky-400" />
          <h3 className="text-sm font-bold text-white tracking-tight">Interactive Glass-Box Simulation Controls</h3>
        </div>

        {/* Playback & Viva Snapshot Actions */}
        <div className="flex items-center space-x-2">
          {/* Play/Pause */}
          <button
            onClick={() => setConfig(prev => ({ ...prev, isPaused: !prev.isPaused }))}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all shadow ${
              config.isPaused
                ? 'bg-emerald-600 hover:bg-emerald-500 text-white'
                : 'bg-slate-800 hover:bg-slate-700 text-slate-200'
            }`}
          >
            {config.isPaused ? <Play className="h-3.5 w-3.5 fill-current" /> : <Pause className="h-3.5 w-3.5 fill-current" />}
            <span>{config.isPaused ? 'Resume Simulation' : 'Pause'}</span>
          </button>

          {/* Speed presets */}
          <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-800 text-[11px] font-mono">
            {[0.5, 1, 2, 5].map((spd) => (
              <button
                key={spd}
                onClick={() => setConfig(prev => ({ ...prev, playbackSpeed: spd }))}
                className={`px-2 py-0.5 rounded-lg transition-colors ${
                  config.playbackSpeed === spd
                    ? 'bg-sky-600 text-white font-bold'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {spd}x
              </button>
            ))}
          </div>

          {/* Academic Snapshot Modal Trigger */}
          <button
            onClick={onOpenSnapshot}
            className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold bg-gradient-to-r from-indigo-500 to-purple-600 text-white hover:from-indigo-400 hover:to-purple-500 shadow-lg shadow-indigo-500/25 transition-all"
          >
            <FileText className="h-3.5 w-3.5" />
            <span>Academic Viva Snapshot</span>
          </button>
        </div>
      </div>

      {/* Preset Scenarios Grid */}
      <div>
        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-2">
          Scenario Presets
        </span>
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
          {[
            { id: 'normal', label: 'Normal Traffic (600 RPS)', color: 'border-slate-700 hover:border-sky-500' },
            { id: 'salary_rush', label: 'Salary Rush (1800 RPS)', color: 'border-slate-700 hover:border-amber-500' },
            { id: 'flash_burst', label: 'Promotional Burst (2800 RPS)', color: 'border-slate-700 hover:border-purple-500' },
            { id: 'chaos_blackout', label: '50% DC Node Crash', color: 'border-slate-700 hover:border-rose-500' },
            { id: 'sqli_attack', label: 'Zero-Trust Attack Probe', color: 'border-slate-700 hover:border-emerald-500' },
          ].map((preset) => {
            const isActive = config.preset === preset.id;
            return (
              <button
                key={preset.id}
                onClick={() => applyPreset(preset.id)}
                className={`px-2.5 py-2 rounded-xl text-xs font-semibold text-left transition-all border ${
                  isActive
                    ? 'bg-sky-500/10 border-sky-500 text-sky-400 shadow-md shadow-sky-500/10'
                    : `bg-slate-950/70 text-slate-300 ${preset.color}`
                }`}
              >
                {preset.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Traffic Slider & Chaos Toggles (2 cols) */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-4 pt-2">
        {/* RPS Slider (6 cols) */}
        <div className="md:col-span-6 bg-slate-950/80 border border-slate-800 rounded-xl p-3.5">
          <div className="flex justify-between items-center mb-2">
            <span className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
              <Zap className="h-3.5 w-3.5 text-amber-400" />
              Incoming Transaction Rate Dial
            </span>
            <span className="font-mono text-sm font-bold text-amber-400">{config.targetRps.toLocaleString()} RPS</span>
          </div>
          
          <input
            type="range"
            min={100}
            max={3000}
            step={50}
            value={config.targetRps}
            onChange={(e) => setConfig(prev => ({ ...prev, targetRps: Number(e.target.value), preset: 'custom' }))}
            className="w-full accent-sky-500 h-2 bg-slate-800 rounded-lg cursor-pointer"
          />

          <div className="flex justify-between text-[10px] font-mono text-slate-500 mt-1">
            <span>100 RPS (Low)</span>
            <span>1,400 RPS (Peak)</span>
            <span>3,000 RPS (Extreme Stress)</span>
          </div>
        </div>

        {/* Live Chaos Injection Matrix (6 cols) */}
        <div className="md:col-span-6 bg-slate-950/80 border border-slate-800 rounded-xl p-3.5">
          <span className="text-xs font-bold text-slate-300 block mb-2">
            Real-Time Chaos Injection Controls
          </span>

          <div className="grid grid-cols-2 gap-2">
            {/* 50% Cores Outage */}
            <button
              onClick={() => setConfig(prev => ({ ...prev, chaosCoreDrop: !prev.chaosCoreDrop }))}
              className={`flex items-center space-x-2 px-2.5 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                config.chaosCoreDrop
                  ? 'bg-rose-500/20 border-rose-500 text-rose-300 animate-pulse'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              <Flame className="h-3.5 w-3.5" />
              <span>50% Core Crash</span>
            </button>

            {/* Network Spike */}
            <button
              onClick={() => setConfig(prev => ({ ...prev, chaosNetworkSpike: !prev.chaosNetworkSpike }))}
              className={`flex items-center space-x-2 px-2.5 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                config.chaosNetworkSpike
                  ? 'bg-amber-500/20 border-amber-500 text-amber-300'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              <Globe className="h-3.5 w-3.5" />
              <span>+25ms Transit Lag</span>
            </button>

            {/* DB Connection Lock */}
            <button
              onClick={() => setConfig(prev => ({ ...prev, chaosDbLock: !prev.chaosDbLock }))}
              className={`flex items-center space-x-2 px-2.5 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                config.chaosDbLock
                  ? 'bg-purple-500/20 border-purple-500 text-purple-300'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              <Database className="h-3.5 w-3.5" />
              <span>DB Pool Lock</span>
            </button>

            {/* Attack Probe */}
            <button
              onClick={() => setConfig(prev => ({ ...prev, chaosAttackProbe: !prev.chaosAttackProbe }))}
              className={`flex items-center space-x-2 px-2.5 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                config.chaosAttackProbe
                  ? 'bg-emerald-500/20 border-emerald-500 text-emerald-300'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              <ShieldAlert className="h-3.5 w-3.5" />
              <span>Inject SQLi Probe</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
