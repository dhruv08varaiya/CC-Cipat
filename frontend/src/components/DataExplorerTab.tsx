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
  const [stats, setStats] = useState<any>(null);

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
    <div className="space-y-6">
      {/* Overview Stat Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="flex items-center space-x-2 text-slate-400 mb-1">
            <Table className="h-4 w-4" />
            <span className="text-xs">Total Tables</span>
          </div>
          <p className="text-xl font-bold text-white">8 Synthetic Tables</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="flex items-center space-x-2 text-slate-400 mb-1">
            <Database className="h-4 w-4" />
            <span className="text-xs">Total Records</span>
          </div>
          <p className="text-xl font-bold text-sky-400">170,000 Rows</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="flex items-center space-x-2 text-slate-400 mb-1">
            <FileText className="h-4 w-4" />
            <span className="text-xs">Workload Traces</span>
          </div>
          <p className="text-xl font-bold text-emerald-400">6 Profiles (W1–W6)</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="flex items-center space-x-2 text-slate-400 mb-1">
            <HardDrive className="h-4 w-4" />
            <span className="text-xs">Storage Format</span>
          </div>
          <p className="text-xl font-bold text-purple-400">CSV & JSONL</p>
        </div>
      </div>

      {/* Table Selector & Paginated Viewer */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
        <div className="flex flex-wrap gap-2 mb-6 pb-4 border-b border-slate-800">
          {datasets.map((d) => {
            const isSelected = selectedTable === d.table_name;
            return (
              <button
                key={d.table_name}
                onClick={() => {
                  setSelectedTable(d.table_name);
                  setPage(1);
                }}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  isSelected
                    ? 'bg-sky-600 text-white shadow-md shadow-sky-600/20'
                    : 'bg-slate-950 text-slate-400 hover:text-white hover:bg-slate-800'
                }`}
              >
                {d.table_name}
              </button>
            );
          })}
        </div>

        {/* Data Table */}
        <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950">
          {loading ? (
            <div className="p-12 text-center text-slate-500 text-xs">Loading table records...</div>
          ) : previewData?.data?.length > 0 ? (
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900 text-slate-300 uppercase font-semibold text-[11px] border-b border-slate-800">
                <tr>
                  {previewData.columns.map((col: string) => (
                    <th key={col} className="p-3 whitespace-nowrap">{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono text-slate-300">
                {previewData.data.map((row: any, i: number) => (
                  <tr key={i} className="hover:bg-slate-900/40">
                    {previewData.columns.map((col: string) => (
                      <td key={col} className="p-3 whitespace-nowrap text-slate-300">
                        {String(row[col])}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="p-12 text-center text-slate-500 text-xs">No records found.</div>
          )}
        </div>

        {/* Pagination Bar */}
        {previewData && (
          <div className="flex items-center justify-between mt-4 text-xs text-slate-400">
            <span>
              Showing Page {previewData.page} of {previewData.total_pages} ({previewData.total_rows?.toLocaleString()} total records)
            </span>
            <div className="flex items-center space-x-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="p-1.5 rounded bg-slate-800 disabled:opacity-40 hover:bg-slate-700"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <button
                disabled={page >= (previewData.total_pages || 1)}
                onClick={() => setPage((p) => p + 1)}
                className="p-1.5 rounded bg-slate-800 disabled:opacity-40 hover:bg-slate-700"
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
