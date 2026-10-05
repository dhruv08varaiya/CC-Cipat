import React, { useState, useEffect } from 'react';
import { 
  Database, 
  FileText, 
  ChevronLeft, 
  ChevronRight, 
  Table, 
  HardDrive 
} from 'lucide-react';
import { 
  fetchDatasetsList, 
  fetchDatasetPreview, 
  fetchDatasetStatistics 
} from '../api/client';

export const DataExplorerTab: React.FC = () => {
  const [datasets, setDatasets] = useState<any[]>([]);
  const [selectedTable, setSelectedTable] = useState('customers');
  const [page, setPage] = useState(1);
  const [previewData, setPreviewData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [, setStats] = useState<any>(null);

  useEffect(() => {
    fetchDatasetsList().then((data) => {
      setDatasets(data);
      if (data.length > 0) setSelectedTable(data[0].table_name);
    });
    fetchDatasetStatistics().then(setStats);
  }, []);

  useEffect(() => {
    if (selectedTable) {
      setLoading(true);
      fetchDatasetPreview(selectedTable, page, 15)
        .then((data) => {
          setPreviewData(data);
          setLoading(false);
        })
        .catch((err) => {
          console.error(err);
          setLoading(false);
        });
    }
  }, [selectedTable, page]);

  return (
    <div className="space-y-3 font-mono">
      {/* Overview Stat Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
        <div className="bg-[#12131A] border border-[#27272A] p-2.5 rounded">
          <div className="flex items-center space-x-2 text-zinc-500 mb-0.5">
            <Table className="h-3.5 w-3.5" />
            <span className="text-[10px]">TOTAL TABLES</span>
          </div>
          <p className="text-sm font-bold text-zinc-100">8 Synthetic</p>
        </div>
        <div className="bg-[#12131A] border border-[#27272A] p-2.5 rounded">
          <div className="flex items-center space-x-2 text-zinc-500 mb-0.5">
            <Database className="h-3.5 w-3.5" />
            <span className="text-[10px]">TOTAL RECORDS</span>
          </div>
          <p className="text-sm font-bold text-sky-400">170,000 Rows</p>
        </div>
        <div className="bg-[#12131A] border border-[#27272A] p-2.5 rounded">
          <div className="flex items-center space-x-2 text-zinc-500 mb-0.5">
            <FileText className="h-3.5 w-3.5" />
            <span className="text-[10px]">WORKLOAD TRACES</span>
          </div>
          <p className="text-sm font-bold text-emerald-400">6 Profiles (W1–W6)</p>
        </div>
        <div className="bg-[#12131A] border border-[#27272A] p-2.5 rounded">
          <div className="flex items-center space-x-2 text-zinc-500 mb-0.5">
            <HardDrive className="h-3.5 w-3.5" />
            <span className="text-[10px]">STORAGE FORMAT</span>
          </div>
          <p className="text-sm font-bold text-purple-400">CSV &amp; JSONL</p>
        </div>
      </div>

      {/* Table Selector & Paginated Viewer */}
      <div className="bg-[#12131A] border border-[#27272A] rounded-md p-3.5 space-y-3">
        <div className="flex flex-wrap gap-1.5 pb-2 border-b border-[#27272A]">
          {datasets.map((d) => {
            const isSelected = selectedTable === d.table_name;
            return (
              <button
                key={d.table_name}
                onClick={() => {
                  setSelectedTable(d.table_name);
                  setPage(1);
                }}
                className={`px-2.5 py-1 rounded text-xs transition-colors ${
                  isSelected
                    ? 'bg-zinc-800 border border-zinc-700 text-zinc-100 font-semibold'
                    : 'bg-[#090A0F] border border-[#27272A] text-zinc-400 hover:text-zinc-200 hover:border-zinc-700'
                }`}
              >
                {d.table_name}
              </button>
            );
          })}
        </div>

        {/* Data Table */}
        <div className="overflow-x-auto rounded border border-[#27272A] bg-[#090A0F]">
          {loading ? (
            <div className="p-8 text-center text-zinc-500 text-xs">Loading table records...</div>
          ) : previewData?.data?.length > 0 ? (
            <table className="w-full text-left text-xs">
              <thead className="bg-[#12131A] text-zinc-500 uppercase text-[10px] border-b border-[#27272A]">
                <tr>
                  {previewData.columns.map((col: string) => (
                    <th key={col} className="p-2 whitespace-nowrap">{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-[#27272A] text-[11px] text-zinc-300">
                {previewData.data.map((row: any, i: number) => (
                  <tr key={i} className="hover:bg-zinc-800/30">
                    {previewData.columns.map((col: string) => (
                      <td key={col} className="p-2 whitespace-nowrap text-zinc-300">
                        {String(row[col])}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="p-8 text-center text-zinc-500 text-xs">No records found.</div>
          )}
        </div>

        {/* Pagination Bar */}
        {previewData && (
          <div className="flex items-center justify-between text-xs text-zinc-400">
            <span className="text-[11px]">
              Page {previewData.page} / {previewData.total_pages} ({previewData.total_rows?.toLocaleString()} records)
            </span>
            <div className="flex items-center space-x-1.5">
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="p-1 rounded bg-[#090A0F] border border-[#27272A] text-zinc-400 disabled:opacity-30 hover:text-white hover:border-zinc-700"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <button
                disabled={page >= (previewData.total_pages || 1)}
                onClick={() => setPage((p) => p + 1)}
                className="p-1 rounded bg-[#090A0F] border border-[#27272A] text-zinc-400 disabled:opacity-30 hover:text-white hover:border-zinc-700"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
