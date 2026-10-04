import React from 'react';
import { 
  Server, 
  Activity, 
  FlaskConical, 
  ShieldCheck, 
  Database, 
  Layers,
  Zap,
  Radio
} from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  const tabs = [
    { id: 'digital_twin', label: 'Living Digital Twin', icon: Radio },
    { id: 'lifecycle', label: 'Action Inspector', icon: Zap },
    { id: 'simulation', label: 'Discrete Sim', icon: Activity },
    { id: 'experiments', label: 'Experiments Lab', icon: FlaskConical },
    { id: 'security', label: 'Security & Compliance', icon: ShieldCheck },
    { id: 'data', label: 'Data Explorer', icon: Database },
    { id: 'overview', label: 'Architecture', icon: Layers },
  ];

  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-sky-500/20">
              <Server className="h-5 w-5 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg text-white tracking-tight">CC-CIPAT</span>
                <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  Real-Time Twin
                </span>
              </div>
              <p className="text-xs text-slate-400">Secure Hybrid Cloud Banking Simulation</p>
            </div>
          </div>

          <nav className="flex space-x-1">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-xs font-semibold transition-all ${
                    isActive
                      ? 'bg-sky-600 text-white shadow-md shadow-sky-600/30'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                  }`}
                >
                  <Icon className="h-3.5 w-3.5" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>
    </header>
  );
};
