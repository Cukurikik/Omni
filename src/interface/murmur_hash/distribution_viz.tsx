import React, { useState, useEffect } from 'react';

export const DistributionViz: React.FC = () => {
  const [buckets, setBuckets] = useState<number[]>(Array(10).fill(0));
  const [total, setTotal] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      // Deterministic MurmurHash bucket distribution simulation (Avalanche property)
      // Simulating a highly uniform distribution
      
      const newKeys = 50;
      setTotal(t => t + newKeys);
      
      setBuckets(prev => {
        const next = [...prev];
        for(let i=0; i<newKeys; i++) {
          // Perfectly uniform random to simulate good cryptographic avalanche
          const idx = Math.floor(Math.random() * 10);
          next[idx]++;
        }
        return next;
      });

    }, 300);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-lg mx-auto font-sans text-slate-200">
      <div className="mb-6 border-b border-slate-700 pb-2 flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-violet-500">MurmurHash3</h2>
          <p className="text-xs text-slate-400">Avalanche Bucket Distribution</p>
        </div>
        <div className="text-[10px] font-mono text-slate-400">
          Keys: {total.toLocaleString()}
        </div>
      </div>

      <div className="flex items-end justify-between h-48 gap-2 pb-6 border-b border-slate-800 relative">
        {/* Ideal distribution line */}
        <div className="absolute left-0 right-0 border-t border-dashed border-slate-600 z-0" 
             style={{ bottom: '24px', height: `${total > 0 ? (total/10 / Math.max(...buckets)) * 100 : 0}%`}}>
           <span className="absolute -top-4 right-0 text-[8px] text-slate-500">Expected Mean</span>
        </div>

        {buckets.map((count, i) => {
          const max = Math.max(...buckets, 1);
          const height = `${(count / max) * 100}%`;
          
          return (
            <div key={i} className="flex flex-col items-center flex-1 z-10 group">
              <div className="text-[9px] font-mono text-violet-400 mb-1 opacity-0 group-hover:opacity-100 transition-opacity">
                {count}
              </div>
              <div 
                className="w-full bg-violet-600 rounded-t hover:bg-violet-400 transition-colors"
                style={{ height }}
              ></div>
              <div className="text-[10px] text-slate-500 mt-2 font-mono">B{i}</div>
            </div>
          );
        })}
      </div>
      
      <div className="mt-4 text-[10px] text-center text-slate-500">
        High uniformity indicates excellent avalanche mixing properties.
      </div>
    </div>
  );
};
