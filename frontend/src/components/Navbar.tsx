import React from 'react';
import { 
  Radio, 
  Layers, 
  Cpu, 
  FlaskConical, 
  ShieldCheck, 
  Database, 
  Info
} from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  const navItems = [
    { id: 'digital_twin', label: 'Digital Twin', icon: Radio },
    { id: 'lifecycle', label: 'Lifecycle', icon: Layers },
    { id: 'simulation', label: 'Simulation', icon: Cpu },
    { id: 'experiments', label: 'Experiments', icon: FlaskConical },
    { id: 'security', label: 'Security', icon: ShieldCheck },
    { id: 'data', label: 'Data', icon: Database },
    { id: 'overview', label: 'Overview', icon: Info },
  ];

  return (
    <header className="sticky top-0 z-50 bg-[#090A0F] border-b border-[#27272A] px-4 sm:px-6">
      <div className="max-w-[1400px] mx-auto flex items-center justify-between h-12">
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <span className="font-mono font-bold text-sm tracking-tight text-zinc-100">
              CC-CIPAT
            </span>
            <span className="font-mono text-[10px] uppercase font-semibold px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-300 border border-zinc-700">
              Simulation Twin
            </span>
          </div>
        </div>

        {/* Tab Navigation */}
        <nav className="flex items-center space-x-1 sm:space-x-2 h-full">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`h-full flex items-center space-x-1.5 px-3 border-b-2 text-xs font-medium transition-colors ${
                  isActive
                    ? 'border-zinc-200 text-zinc-100 bg-zinc-900/50'
                    : 'border-transparent text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/30'
                }`}
              >
                <Icon className={`h-3.5 w-3.5 ${isActive ? 'text-zinc-100' : 'text-zinc-500'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Status Indicator */}
        <div className="hidden sm:flex items-center space-x-2">
          <div className="flex items-center space-x-1.5 px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-mono text-[11px]">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>SimPy 4.1</span>
          </div>
        </div>
      </div>
    </header>
  );
};
