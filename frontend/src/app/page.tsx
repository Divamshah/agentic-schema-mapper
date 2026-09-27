"use client";

import { useState } from "react";
import { UploadCloud, Code, Table as TableIcon, Loader2 } from "lucide-react";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [plan, setPlan] = useState<any>(null);
  const [data, setData] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const processFile = async () => {
    if (!file) return;
    setIsLoading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append("file", file);

    try {
      // Assuming FastAPI runs on 8000
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/process-csv`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error(await res.text());
      }

      const result = await res.json();
      setPlan(result.plan);
      setData(result.data);
    } catch (err: any) {
      setError(err.message || "An error occurred connecting to the backend.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 text-gray-900 font-sans selection:bg-blue-100 pb-20">
      <div className="max-w-7xl mx-auto px-4 py-12 space-y-8">
        
        {/* Header */}
        <header className="flex flex-col items-center justify-center space-y-4 text-center mb-12">
          <div className="inline-flex items-center px-3 py-1 rounded-full bg-blue-50 border border-blue-100 text-blue-700 text-xs font-semibold mb-2">
            Agentic ETL Mapper
          </div>
          <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">
            Agentic Schema Mapper
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mt-4">
            Upload messy ERP exports. Watch the AI build a deterministic mapping plan, and see the clean canonical ledger magically appear.
          </p>
        </header>

        {/* Upload Section */}
        <section className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 flex flex-col items-center justify-center space-y-6">
          <label className="flex flex-col items-center justify-center w-full max-w-xl h-48 border-2 border-dashed border-blue-200 rounded-xl cursor-pointer bg-blue-50/30 hover:bg-blue-50 transition-colors">
            <div className="flex flex-col items-center justify-center pt-5 pb-6">
              <UploadCloud className="w-12 h-12 mb-3 text-blue-500" />
              <p className="mb-2 text-sm text-gray-700">
                <span className="font-semibold text-blue-600">Click to upload</span> or drag and drop
              </p>
              <p className="text-xs text-gray-500">Any messy ERP CSV file (.csv)</p>
            </div>
            <input type="file" className="hidden" accept=".csv" onChange={handleFileUpload} />
          </label>

          {file && (
            <div className="flex items-center space-x-4 bg-gray-50 pr-2 pl-4 py-2 rounded-xl border border-gray-200">
              <span className="text-sm font-medium text-gray-700">
                📄 {file.name}
              </span>
              <button 
                onClick={processFile}
                disabled={isLoading}
                className="px-6 py-2 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 transition-colors shadow-sm disabled:opacity-50 flex items-center space-x-2"
              >
                {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
                <span>{isLoading ? "AI is processing..." : "Process with Agent"}</span>
              </button>
            </div>
          )}

          {error && <div className="text-red-600 text-sm font-medium bg-red-50 border border-red-100 px-4 py-3 rounded-lg w-full max-w-xl text-center">{error}</div>}
        </section>

        {/* Split Pane View */}
        {(plan || data.length > 0) && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start pt-8">
            
            {/* Left Pane: JSON Plan */}
            <div className="bg-slate-900 rounded-2xl shadow-xl overflow-hidden border border-slate-800 ring-1 ring-white/10">
              <div className="flex items-center px-5 py-4 bg-slate-950 border-b border-slate-800">
                <Code className="w-5 h-5 text-emerald-400 mr-3" />
                <h2 className="text-sm font-bold text-slate-200 tracking-wide">THE BRAIN (EXTRACTION PLAN)</h2>
              </div>
              <div className="p-5 overflow-auto max-h-[600px] text-xs font-mono text-blue-300 leading-relaxed custom-scrollbar">
                <pre>{JSON.stringify(plan, null, 2)}</pre>
              </div>
            </div>

            {/* Right Pane: Canonical Data */}
            <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-200 ring-1 ring-black/5">
              <div className="flex items-center px-5 py-4 bg-gray-50 border-b border-gray-200">
                <TableIcon className="w-5 h-5 text-indigo-600 mr-3" />
                <h2 className="text-sm font-bold text-gray-800 tracking-wide">THE MUSCLE (CANONICAL LEDGER)</h2>
                <span className="ml-auto text-xs font-bold bg-indigo-100 text-indigo-700 px-3 py-1 rounded-full shadow-sm">
                  {data.length} Rows
                </span>
              </div>
              <div className="overflow-auto max-h-[600px] custom-scrollbar">
                <table className="w-full text-sm text-left text-gray-600">
                  <thead className="text-xs text-gray-500 uppercase bg-gray-50 sticky top-0 border-b border-gray-200 z-10 shadow-sm">
                    <tr>
                      <th className="px-5 py-4 font-semibold">Txn ID</th>
                      <th className="px-5 py-4 font-semibold">Date</th>
                      <th className="px-5 py-4 font-semibold">Account</th>
                      <th className="px-5 py-4 font-semibold text-center">Direction</th>
                      <th className="px-5 py-4 font-semibold text-right">Amount</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {data.map((row, i) => (
                      <tr key={i} className="hover:bg-blue-50/30 transition-colors">
                        <td className="px-5 py-3 font-medium text-gray-900 whitespace-nowrap">{row.transaction_id}</td>
                        <td className="px-5 py-3 whitespace-nowrap">{row.date}</td>
                        <td className="px-5 py-3 truncate max-w-[150px]" title={row.account_name}>{row.account_name}</td>
                        <td className="px-5 py-3 text-center">
                          <span className={`inline-flex items-center justify-center px-2.5 py-1 rounded-md text-xs font-bold ${
                            row.direction === 'DEBIT' 
                              ? 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-600/20' 
                              : 'bg-rose-50 text-rose-700 ring-1 ring-rose-600/20'
                          }`}>
                            {row.direction}
                          </span>
                        </td>
                        <td className="px-5 py-3 text-right font-mono font-medium text-gray-900 whitespace-nowrap">
                          {row.currency} {row.amount.toFixed(2)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

          </div>
        )}
      </div>
      
      {/* Small custom styles for scrollbar embedded directly */}
      <style dangerouslySetInnerHTML={{__html: `
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
          height: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background-color: rgba(156, 163, 175, 0.5);
          border-radius: 20px;
        }
      `}} />
    </main>
  );
}
