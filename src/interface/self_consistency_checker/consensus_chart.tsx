import React, { useState, useEffect } from 'react';

export const ConsensusChart: React.FC = () => {
  const [samples, setSamples] = useState(0);
  const [consensus, setConsensus] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setSamples(prev => {
        if (prev >= 10) {
           setConsensus(true);
           clearInterval(interval);
           return prev;
        }
        return prev + 1;
      });
    }, 400);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-sky-400">Self-Consistency</h2>
          <p className="text-xs text-slate-400">Majority Vote Sampling</p>
        </div>
        <div className="text-xs font-mono bg-slate-800 px-2 py-1 rounded text-slate-300">
          K={samples}/10
        </div>
      </div>

      <div className="space-y-3 font-mono text-xs">
         <div className="flex items-center gap-2">
            <span className="w-16 text-right">Ans: A</span>
            <div className="flex-1 h-3 bg-slate-800 rounded overflow-hidden">
               <div className="h-full bg-sky-500 transition-all duration-300" style={{ width: `${(Math.min(samples, 7) / 10) * 100}%` }}></div>
            </div>
            <span className="w-8">70%</span>
         </div>
         
         <div className="flex items-center gap-2">
            <span className="w-16 text-right">Ans: B</span>
            <div className="flex-1 h-3 bg-slate-800 rounded overflow-hidden">
               <div className="h-full bg-slate-500 transition-all duration-300" style={{ width: `${(Math.min(samples, 2) / 10) * 100}%` }}></div>
            </div>
            <span className="w-8">20%</span>
         </div>

         <div className="flex items-center gap-2">
            <span className="w-16 text-right">Ans: C</span>
            <div className="flex-1 h-3 bg-slate-800 rounded overflow-hidden">
               <div className="h-full bg-slate-500 transition-all duration-300" style={{ width: `${(samples >= 10 ? 1 : 0) / 10 * 100}%` }}></div>
            </div>
            <span className="w-8">10%</span>
         </div>
      </div>
      
      {consensus && (
         <div className="mt-6 p-3 bg-sky-900/30 border border-sky-800 rounded text-center animate-fade-in shadow-[0_0_15px_rgba(14,165,233,0.15)]">
            <div className="text-[10px] uppercase font-bold text-sky-500 mb-1">Consensus Reached</div>
            <div className="text-white text-sm">Output: Answer A</div>
         </div>
      )}
    </div>
  );
};
