import React, { useState, useEffect } from 'react';

export const NoiseInspector: React.FC = () => {
  const [samples, setSamples] = useState<{id: string, given: string, pred: string, margin: number, isNoisy: boolean}[]>([]);

  useEffect(() => {
    // Deterministic Cleanlab Noise inspection stream
    let count = 0;
    const interval = setInterval(() => {
      count++;
      
      // Generating pseudo-realistic deterministic data
      const isNoise = count % 7 === 0;
      const given = isNoise ? 'Dog' : 'Cat';
      const pred = 'Cat';
      const margin = isNoise ? -0.45 : 0.65; // Negative margin triggers noise

      setSamples(prev => {
        const next = [{ id: `IMG_${count.toString().padStart(4, '0')}`, given, pred, margin, isNoisy: isNoise }, ...prev];
        return next.slice(0, 10); // Keep last 10
      });

    }, 800);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-50 p-6 rounded-lg border border-slate-200 shadow-xl max-w-2xl mx-auto font-sans">
      <div className="mb-6 border-b border-slate-200 pb-2 flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-indigo-600">Cleanlab Inspector</h2>
          <p className="text-xs text-slate-500">Confident Learning Label Errors</p>
        </div>
        <div className="bg-white border border-slate-200 px-3 py-1 rounded shadow-sm flex items-center gap-2">
           <div className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse"></div>
           <span className="text-[10px] font-bold text-slate-600">LIVE STREAM</span>
        </div>
      </div>

      <div className="overflow-hidden rounded border border-slate-200 shadow-sm bg-white">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-100 text-slate-600 border-b border-slate-200">
            <tr>
              <th className="p-3 font-bold text-xs">Sample ID</th>
              <th className="p-3 font-bold text-xs">Given Label</th>
              <th className="p-3 font-bold text-xs">Predicted</th>
              <th className="p-3 font-bold text-xs">Margin</th>
              <th className="p-3 font-bold text-xs">Status</th>
            </tr>
          </thead>
          <tbody>
            {samples.map((s, i) => (
              <tr key={s.id} className="border-b border-slate-50 hover:bg-slate-50 transition-colors">
                <td className="p-3 font-mono text-xs text-slate-500">{s.id}</td>
                <td className={`p-3 font-bold ${s.isNoisy ? 'text-rose-500 line-through' : 'text-slate-700'}`}>{s.given}</td>
                <td className="p-3 font-bold text-emerald-600">{s.pred}</td>
                <td className="p-3 font-mono text-xs text-slate-600">{s.margin.toFixed(2)}</td>
                <td className="p-3">
                  {s.isNoisy ? 
                    <span className="bg-rose-100 text-rose-700 px-2 py-1 rounded text-[10px] font-bold">ERROR</span> : 
                    <span className="bg-emerald-100 text-emerald-700 px-2 py-1 rounded text-[10px] font-bold">CLEAN</span>
                  }
                </td>
              </tr>
            ))}
            {samples.length === 0 && (
              <tr><td colSpan={5} className="p-6 text-center text-slate-400 text-xs">Awaiting data stream...</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
