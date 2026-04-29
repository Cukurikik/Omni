import React, { useState, useEffect } from 'react';

export const RatioMonitor: React.FC = () => {
  const [chunks, setChunks] = useState<{id: number, orig: number, comp: number}[]>([]);
  const [totals, setTotals] = useState({ orig: 0, comp: 0 });

  useEffect(() => {
    let id = 0;
    const interval = setInterval(() => {
      id++;
      
      // Deterministic Snappy compression simulation (approx 40-60% size reduction)
      const orig = 32768; // 32KB chunk
      const ratio = 0.4 + (Math.random() * 0.3); // 40% to 70% of original
      const comp = Math.floor(orig * ratio);

      setTotals(t => ({ orig: t.orig + orig, comp: t.comp + comp }));

      setChunks(prev => {
        const next = [{ id, orig, comp }, ...prev];
        return next.slice(0, 5);
      });
    }, 500);

    return () => clearInterval(interval);
  }, []);

  const overallRatio = totals.orig > 0 ? ((totals.comp / totals.orig) * 100).toFixed(1) : '0.0';

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 border-b border-slate-700 pb-2 flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-sky-400">Snappy Flow</h2>
          <p className="text-xs text-slate-400">Live Block Compression</p>
        </div>
        <div className="text-2xl font-black font-mono text-emerald-400">
          {overallRatio}%
        </div>
      </div>

      <div className="flex flex-col gap-3">
        {chunks.map(c => {
          const ratio = (c.comp / c.orig) * 100;
          return (
            <div key={c.id} className="bg-slate-800 p-3 rounded border border-slate-700">
              <div className="flex justify-between text-xs font-bold text-slate-400 mb-2">
                <span>Block #{c.id}</span>
                <span>{ratio.toFixed(1)}% Ratio</span>
              </div>
              
              {/* Uncompressed Bar */}
              <div className="flex items-center gap-2 mb-1">
                 <div className="text-[9px] w-10 text-slate-500 uppercase">RAW</div>
                 <div className="h-2 bg-slate-600 flex-1 rounded overflow-hidden">
                    <div className="h-full bg-slate-400 w-full"></div>
                 </div>
              </div>
              
              {/* Compressed Bar */}
              <div className="flex items-center gap-2">
                 <div className="text-[9px] w-10 text-slate-500 uppercase">LZ77</div>
                 <div className="h-2 bg-slate-600 flex-1 rounded overflow-hidden">
                    <div className="h-full bg-sky-500" style={{width: `${ratio}%`}}></div>
                 </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
