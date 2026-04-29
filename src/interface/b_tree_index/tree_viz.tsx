import React, { useState, useEffect } from 'react';

export const TreeViz: React.FC = () => {
  const [rootKeys, setRootKeys] = useState<number[]>([10, 40]);
  const [degree] = useState(3); // Max 5 keys per node
  
  useEffect(() => {
    const interval = setInterval(() => {
      setRootKeys(prev => {
        const next = [...prev];
        const newKey = Math.floor(Math.random() * 100);
        
        if (!next.includes(newKey)) {
          next.push(newKey);
          next.sort((a,b) => a - b);
        }
        
        // Split math: Max keys = 2t - 1 = 5
        if (next.length > 5) {
          // Simulate root split (push median up, which makes a new root in reality)
          // For visualization, we just clear and "split"
          return [next[2]]; 
        }
        
        return next;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 flex justify-between items-center border-b border-slate-700 pb-3">
        <div>
          <h2 className="text-xl font-bold text-blue-400">B-Tree Index</h2>
          <p className="text-xs text-slate-400">Database Page Splits</p>
        </div>
        <div className="text-[10px] font-mono bg-slate-800 px-2 py-1 rounded text-slate-400 border border-slate-700">
          t={degree} (Max 5 Keys)
        </div>
      </div>

      <div className="flex flex-col items-center justify-center min-h-[120px]">
        
        <div className={`flex border-2 rounded ${rootKeys.length >= 5 ? 'border-red-500 shadow-[0_0_10px_#ef4444]' : 'border-blue-500'}`}>
          {rootKeys.map((k, i) => (
            <div key={k} className={`w-10 h-10 flex items-center justify-center font-mono font-bold text-sm
              ${i < rootKeys.length - 1 ? 'border-r-2 border-slate-700' : ''}
              ${rootKeys.length >= 5 ? 'bg-red-900/30 text-red-200' : 'bg-slate-800 text-blue-200'}
            `}>
              {k}
            </div>
          ))}
          {/* Fill empty slots */}
          {Array(5 - rootKeys.length).fill(0).map((_, i) => (
            <div key={`e${i}`} className={`w-10 h-10 border-slate-800 bg-slate-950
              ${i < (4 - rootKeys.length) ? 'border-r-2' : ''}
            `}></div>
          ))}
        </div>

        {rootKeys.length >= 5 && (
          <div className="text-xs font-bold text-red-500 mt-4 animate-bounce uppercase tracking-widest">
            Page Split Imminent!
          </div>
        )}
      </div>
    </div>
  );
};
