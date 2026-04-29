import React, { useState, useEffect } from 'react';

export const RagDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState({
    mrr: 0.85,
    latency: 120,
    chunks: 1450000
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(prev => ({
        mrr: Math.min(0.99, prev.mrr + (Math.random() * 0.02 - 0.01)),
        latency: Math.max(50, prev.latency + (Math.random() * 10 - 6)),
        chunks: prev.chunks + Math.floor(Math.random() * 100)
      }));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 border-b border-slate-700 pb-2">
        <h2 className="text-xl font-bold text-indigo-400">Awesome RAG</h2>
        <p className="text-xs text-slate-400">Retrieval Augmented Generation Orchestrator</p>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-slate-950 p-3 rounded border border-slate-800">
          <div className="text-[10px] text-slate-500 uppercase font-bold">Vector Chunks</div>
          <div className="text-lg font-mono text-white">{(metrics.chunks / 1000000).toFixed(2)}M</div>
        </div>
        <div className="bg-slate-950 p-3 rounded border border-slate-800">
          <div className="text-[10px] text-slate-500 uppercase font-bold">Avg Latency</div>
          <div className="text-lg font-mono text-amber-400">{metrics.latency.toFixed(0)}ms</div>
        </div>
      </div>

      <div>
        <div className="flex justify-between text-xs mb-1">
          <span className="text-slate-400">Mean Reciprocal Rank (MRR)</span>
          <span className="font-mono text-indigo-300">{metrics.mrr.toFixed(3)}</span>
        </div>
        <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
          <div 
            className="bg-indigo-500 h-full transition-all duration-300" 
            style={{ width: `${metrics.mrr * 100}%` }}
          />
        </div>
      </div>
    </div>
  );
};
