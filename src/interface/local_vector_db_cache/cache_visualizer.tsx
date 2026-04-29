import React, { useState, useEffect } from 'react';

export const CacheVisualizer: React.FC = () => {
  const [hits, setHits] = useState(0);
  const [misses, setMisses] = useState(0);
  const [lastAction, setLastAction] = useState<'hit' | 'miss' | null>(null);

  useEffect(() => {
    const interval = setInterval(() => {
      // 75% hit rate simulation
      if (Math.random() > 0.25) {
        setHits(h => h + 1);
        setLastAction('hit');
      } else {
        setMisses(m => m + 1);
        setLastAction('miss');
      }
      
      setTimeout(() => setLastAction(null), 300);
    }, 600);
    return () => clearInterval(interval);
  }, []);

  const total = hits + misses || 1;
  const hitRate = ((hits / total) * 100).toFixed(1);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-teal-400">Vector Cache</h2>
          <p className="text-xs text-slate-400">Local LRU Memory</p>
        </div>
        <div className="text-xl font-mono text-white bg-slate-800 px-2 rounded">
           {hitRate}%
        </div>
      </div>

      <div className="flex gap-4 mb-4">
         <div className={`flex-1 bg-slate-950 p-4 rounded border transition-colors duration-300 text-center ${lastAction === 'hit' ? 'border-teal-500 bg-teal-900/20' : 'border-slate-800'}`}>
            <div className="text-2xl font-mono text-teal-400">{hits}</div>
            <div className="text-[10px] uppercase text-slate-500 mt-1">Cache Hits</div>
         </div>
         <div className={`flex-1 bg-slate-950 p-4 rounded border transition-colors duration-300 text-center ${lastAction === 'miss' ? 'border-amber-500 bg-amber-900/20' : 'border-slate-800'}`}>
            <div className="text-2xl font-mono text-amber-400">{misses}</div>
            <div className="text-[10px] uppercase text-slate-500 mt-1">Cache Misses</div>
         </div>
      </div>

      <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden flex">
         <div className="h-full bg-teal-500 transition-all duration-300" style={{ width: `${hitRate}%` }}></div>
         <div className="h-full bg-amber-500 transition-all duration-300" style={{ width: `${100 - parseFloat(hitRate)}%` }}></div>
      </div>
      
      {parseFloat(hitRate) < 50 && total > 5 && (
         <div className="mt-4 p-2 bg-amber-950/50 border border-amber-900 rounded text-[10px] text-amber-300 flex items-center gap-2 animate-pulse">
            <span>⚠️</span> Hit rate critically low. Triggering cloud prefetch...
         </div>
      )}
    </div>
  );
};
