import React, { useState, useEffect } from 'react';

export const TimelinePruner: React.FC = () => {
  const [branches, setBranches] = useState<number[]>(Array(10).fill(1)); // 1 = Alive, 0 = Pruned
  const [totalPruned, setTotalPruned] = useState(0);
  const [paradoxDetected, setParadoxDetected] = useState<number | null>(null);

  useEffect(() => {
    // Simulate multiverse branching and paradox generation
    const pruner = setInterval(() => {
       // Randomly generate a paradox in a live branch
       const liveIndexes = branches.map((status, idx) => status === 1 ? idx : -1).filter(idx => idx !== -1);
       
       if (liveIndexes.length > 0 && Math.random() > 0.7) {
          const targetIdx = liveIndexes[Math.floor(Math.random() * liveIndexes.length)];
          setParadoxDetected(targetIdx);
          
          // Auto-prune after a short delay
          setTimeout(() => {
             setBranches(prev => {
                const newBranches = [...prev];
                newBranches[targetIdx] = 0;
                return newBranches;
             });
             setTotalPruned(prev => prev + 1);
             setParadoxDetected(null);
          }, 600);
       }
       
       // Regenerate a branch if we run low
       if (liveIndexes.length < 5 && Math.random() > 0.5) {
          setBranches(prev => {
             const newBranches = [...prev];
             const deadIndex = newBranches.indexOf(0);
             if (deadIndex !== -1) newBranches[deadIndex] = 1;
             return newBranches;
          });
       }

    }, 1000);

    return () => clearInterval(pruner);
  }, [branches]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-orange-500">Everett Pruner</h2>
          <p className="text-xs text-slate-400">Timeline Decoherence</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-bold border ${paradoxDetected !== null ? 'bg-red-900/80 text-white border-red-500 shadow-[0_0_15px_#ef4444] animate-pulse' : 'bg-slate-800 text-orange-400 border-slate-700'}`}>
          {paradoxDetected !== null ? 'PARADOX DETECTED' : 'TIMELINES STABLE'}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex flex-col justify-end items-center shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* The Multiverse Tree / Timelines */}
         <div className="relative w-full h-[150%] flex justify-center items-end opacity-80" style={{ transformOrigin: 'bottom', transform: 'scale(0.8)' }}>
            
            {/* Trunk (Primary Timeline) */}
            <div className="absolute bottom-0 w-2 h-32 bg-orange-400 shadow-[0_0_15px_#f97316]"></div>
            
            {/* Branches */}
            {branches.map((status, i) => {
               const angle = -60 + (i * 12);
               const height = 60 + Math.abs(angle);
               const isParadox = paradoxDetected === i;
               
               return (
                  <div 
                     key={i}
                     className={`absolute bottom-24 w-1 transition-all duration-500 origin-bottom ${status === 1 ? 'bg-orange-300 shadow-[0_0_10px_#fdba74]' : 'bg-slate-700 opacity-30'} ${isParadox ? 'bg-red-500 shadow-[0_0_20px_#ef4444] animate-pulse' : ''}`}
                     style={{
                        height: `${height}px`,
                        transform: `rotate(${angle}deg)`,
                     }}
                  >
                     {/* Decoherence Flash */}
                     {status === 0 && (
                        <div className="absolute top-0 w-4 h-4 -ml-1.5 rounded-full bg-red-500/20 mix-blend-screen opacity-0 animate-[ping_0.5s_ease-out]"></div>
                     )}
                  </div>
               );
            })}
         </div>

         {/* Pruning Laser */}
         {paradoxDetected !== null && (
            <div className="absolute top-0 w-full h-1 bg-white shadow-[0_0_20px_#fff] mix-blend-screen animate-bounce"></div>
         )}
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Active Branches</div>
            <div className="text-lg font-mono font-bold text-orange-400">
               {branches.filter(s => s === 1).length} <span className="text-xs text-slate-500">/ {branches.length}</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Total Pruned</div>
            <div className="text-lg font-mono font-bold text-slate-300">
               {totalPruned}
            </div>
         </div>
      </div>

      <div className="w-full bg-slate-950 rounded border border-slate-800 p-2 text-[10px] font-mono text-center">
         <span className={paradoxDetected !== null ? 'text-red-400 font-bold' : 'text-emerald-400'}>
            {paradoxDetected !== null 
               ? `CAUSALITY VIOLATION IN BRANCH ${paradoxDetected} - SEVERING...` 
               : 'MANY-WORLDS TREE GROWING NOMINALLY'}
         </span>
      </div>
    </div>
  );
};
