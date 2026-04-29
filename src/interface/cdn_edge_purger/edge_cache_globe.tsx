import React, { useState, useEffect } from 'react';

export const EdgeCacheGlobe: React.FC = () => {
  const [hitRate, setHitRate] = useState(98.5);
  const [purging, setPurging] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate cache hit rate fluctuations
      if (!purging) {
         setHitRate(prev => Math.min(99.9, prev + (Math.random() * 0.1)));
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [purging]);

  const handlePurge = () => {
      if (purging) return;
      setPurging(true);
      // Simulating the massive hit-rate drop when global cache is purged
      setHitRate(45.2);
      
      // Simulating cache slowly rebuilding
      let ticks = 0;
      const rebuild = setInterval(() => {
         ticks++;
         setHitRate(prev => Math.min(98.5, prev + (Math.random() * 5 + 2)));
         if (ticks > 15) {
            clearInterval(rebuild);
            setPurging(false);
         }
      }, 500);
  };

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-teal-400">CDN Edge</h2>
          <p className="text-xs text-slate-400">Global Point-of-Presence</p>
        </div>
        <button 
          onClick={handlePurge}
          disabled={purging}
          className={`px-3 py-1 rounded text-[10px] font-bold uppercase transition-all
            ${purging ? 'bg-slate-800 text-slate-500 cursor-not-allowed' : 'bg-rose-900/50 text-rose-400 border border-rose-800 hover:bg-rose-800/50'}
          `}
        >
          {purging ? 'Purging...' : 'Purge Cache'}
        </button>
      </div>

      <div className="bg-slate-950 p-6 rounded border border-slate-800 flex flex-col items-center justify-center mb-4 relative overflow-hidden">
         <div className="text-[10px] uppercase font-bold text-slate-500 mb-2 z-10">Global Hit Ratio</div>
         <div className={`text-5xl font-mono font-bold z-10 drop-shadow-md transition-colors duration-500
            ${hitRate > 90 ? 'text-teal-400' : hitRate > 70 ? 'text-yellow-400' : 'text-rose-500'}
         `}>
            {hitRate.toFixed(1)}%
         </div>
         
         {/* Background Pulse representing Origin Load */}
         <div 
           className="absolute bottom-0 left-0 w-full bg-rose-500/20 transition-all duration-500 z-0"
           style={{ height: `${100 - hitRate}%` }}
         ></div>
      </div>
      
      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded border border-slate-700">
         <span>Edge Nodes: 342</span>
         <span>Latency: 14ms</span>
         <span className="col-span-2">Origin Load: <span className={hitRate < 80 ? 'text-rose-400 font-bold' : 'text-teal-400'}>
            {((100 - hitRate) * 1200).toFixed(0)} req/s
         </span></span>
      </div>
    </div>
  );
};
