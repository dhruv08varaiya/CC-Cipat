import React, { useState } from 'react';
import { X, Copy, Check, FileCode, Database } from 'lucide-react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  latexCode: string;
  csvData: string;
}

export const AcademicSnapshotModal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  latexCode,
  csvData,
}) => {
  const [activeTab, setActiveTab] = useState<'latex' | 'csv'>('latex');
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const currentContent = activeTab === 'latex' ? latexCode : csvData;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(currentContent);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy to clipboard', err);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div className="bg-[#12131A] border border-[#27272A] rounded-md max-w-3xl w-full max-h-[85vh] flex flex-col shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-[#27272A]">
          <div>
            <h3 className="text-xs font-mono font-bold text-zinc-100 uppercase tracking-wider">
              Academic Telemetry Snapshot Export
            </h3>
            <p className="text-[11px] font-mono text-zinc-500 mt-0.5">
              Deterministic state capture for IEEE LaTeX table formatting or CSV statistical analysis
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Tab & Action Bar */}
        <div className="flex items-center justify-between px-4 py-2 bg-[#090A0F] border-b border-[#27272A]">
          <div className="flex space-x-1">
            <button
              onClick={() => setActiveTab('latex')}
              className={`flex items-center space-x-1.5 px-3 py-1 rounded text-xs font-mono transition-colors ${
                activeTab === 'latex'
                  ? 'bg-zinc-800 text-zinc-100 font-semibold'
                  : 'text-zinc-500 hover:text-zinc-300'
              }`}
            >
              <FileCode className="h-3.5 w-3.5" />
              <span>IEEE LaTeX Table</span>
            </button>
            <button
              onClick={() => setActiveTab('csv')}
              className={`flex items-center space-x-1.5 px-3 py-1 rounded text-xs font-mono transition-colors ${
                activeTab === 'csv'
                  ? 'bg-zinc-800 text-zinc-100 font-semibold'
                  : 'text-zinc-500 hover:text-zinc-300'
              }`}
            >
              <Database className="h-3.5 w-3.5" />
              <span>Raw CSV Dataset</span>
            </button>
          </div>

          <button
            onClick={handleCopy}
            className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-200 border border-zinc-700 text-xs font-mono transition-colors"
          >
            {copied ? (
              <>
                <Check className="h-3.5 w-3.5 text-emerald-400" />
                <span className="text-emerald-400">Copied</span>
              </>
            ) : (
              <>
                <Copy className="h-3.5 w-3.5" />
                <span>Copy</span>
              </>
            )}
          </button>
        </div>

        {/* Code Content */}
        <div className="flex-1 p-4 overflow-auto bg-[#090A0F]">
          <pre className="text-xs font-mono text-zinc-300 whitespace-pre-wrap leading-relaxed select-all">
            {currentContent}
          </pre>
        </div>
      </div>
    </div>
  );
};
