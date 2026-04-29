import React, { useState, useEffect } from 'react';

export const CausalityTree: React.FC = () => {
  const [divergence, setDivergence] = useState(0);
  const [branches, setBranches] = useState<number[]>([]);
  const [paradoxAlert, setParadoxAlert] = useState(false);

  useEffect(() => {
    // Simulate timeline progression and branching
    const timeflow = setInterval(() => {
       if (divergence < 100) {
          // Increase timeline divergence
          setDivergence(prev => {
             const next = prev + (Math.random() * 2);
             if (next > 45) setParadoxAlert(true);
             return Math.min(100, next);
          });
          
          // Randomly spawn new timeline branches (Many-worlds)
          if (Math.random() > 0.7 && branches.length < 15) {
             setBranches(prev => [...prev, Math.random() * 100]);
          }
       }
    }, 200);

    return () => clearInterval(timeflow);
  }, [divergence, branches.length]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-teal-300">Causality Engine</h2>
          <p className="text-xs text-slate-400">Everett Multiverse Matrix</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-bold border ${paradoxAlert ? 'bg-red-900/80 text-white border-red-500 shadow-[0_0_15px_#ef4444] animate-pulse' : 'bg-slate-800 text-slate-400 border-slate-700'}`}>
          {paradoxAlert ? 'PARADOX DETECTED' : 'TIMELINE SECURE'}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex items-center justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* Main Timeline Trunk */}
         <div className="absolute left-0 right-0 h-2 bg-gradient-to-r from-teal-900 via-teal-500 to-white shadow-[0_0_15px_#14b8a6]">
            
            {/* Current "Now" indicator moving right */}
            <div 
               className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full shadow-[0_0_20px_#fff]"
               style={{ left: `${divergence}%` }}
            ></div>
         </div>

         {/* Multiverse Branches */}
         {branches.map((b, i) => {
            const isUp = i % 2 === 0;
            return (
               <div 
                  key={i}
                  className="absolute h-1 bg-teal-400/50 shadow-[0_0_5px_#2dd4bf] transition-all duration-1000"
                  style={{
                     left: `${b}%`,
                     width: `${Math.max(0, divergence - b)}%`, // Grow as time passes
                     top: isUp ? 'calc(50% - 1px)' : 'auto',
                     bottom: !isUp ? 'calc(50% - 1px)' : 'auto',
                     transformOrigin: 'left',
                     transform: `rotate(${isUp ? -30 : 30}deg)`
                  }}
               >
                  {/* Branch nodes */}
                  <div className="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-2 bg-teal-200 rounded-full"></div>
               </div>
            );
         })}

         {/* Paradox Warning overlay (screen glitch) */}
         {paradoxAlert && (
            <div className="absolute inset-0 bg-red-500/10 mix-blend-color-burn pointer-events-none animate-pulse">
               {[...Array(5)].map((_, i) => (
                  <div key={i} className="w-full h-1 bg-white/20 mb-2" style={{ transform: `translateX(${Math.random() * 10 - 5}px)` }}></div>
               ))}
            </div>
         )}
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Timeline Divergence</div>
            <div className={`text-lg font-mono font-bold ${paradoxAlert ? 'text-red-400' : 'text-teal-400'}`}>
               {divergence.toFixed(1)} <span className="text-xs">%</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Parallel Realities</div>
            <div className="text-lg font-mono font-bold text-white">
               {branches.length + 1} <span className="text-[8px] text-teal-400">branches</span>
            </div>
         </div>
      </div>

      <div className="w-full bg-slate-950 rounded border border-slate-800 p-2 text-xs font-mono text-center">
         <span className={paradoxAlert ? 'text-red-400 animate-pulse' : 'text-emerald-400'}>
            {paradoxAlert ? 'CHRONOLOGY PROTECTION FAILING' : 'CAUSALITY LOOPS RESOLVED'}
         </span>
      </div>
    </div>
  );
};
