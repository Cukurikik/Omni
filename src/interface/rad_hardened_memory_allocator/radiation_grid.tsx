import React, { useState, useEffect } from 'react';

export const RadiationGrid: React.FC = () => {
  const [grid, setGrid] = useState<boolean[]>(Array(64).fill(false));
  const [fixedCount, setFixedCount] = useState(0);

  useEffect(() => {
    // Simulate cosmic ray strikes (bit flips)
    const strikeInterval = setInterval(() => {
      setGrid(prev => {
         const next = [...prev];
         const randomIndex = Math.floor(Math.random() * 64);
         next[randomIndex] = true; // Flip bit
         return next;
      });
    }, 800);

    // Simulate background ECC scrubber fixing them
    const scrubInterval = setInterval(() => {
      setGrid(prev => {
         const next = [...prev];
         let fixed = false;
         for (let i=0; i<64; i++) {
            if (next[i]) {
               next[i] = false; // Fix bit
               setFixedCount(c => c + 1);
               fixed = true;
               break; // Fix one per cycle
            }
         }
         return next;
      });
    }, 400); // Scrubber is twice as fast as the average strike rate

    return () => { clearInterval(strikeInterval); clearInterval(scrubInterval); };
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-purple-400">Memory Scrub</h2>
          <p className="text-xs text-slate-400">Rad-Hardened ECC Matrix</p>
        </div>
        <div className="text-[10px] font-mono bg-purple-900/30 text-purple-400 border border-purple-800 px-2 py-1 rounded">
          TMR Active
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 flex items-center justify-center">
         
         {/* Visual 8x8 RAM Grid */}
         <div className="grid grid-cols-8 gap-1">
            {grid.map((isFlipped, i) => (
               <div 
                 key={i} 
                 className={`w-4 h-4 rounded-sm transition-colors duration-150
                   ${isFlipped ? 'bg-red-500 shadow-[0_0_8px_#ef4444]' : 'bg-emerald-900 border border-emerald-800/50'}
                 `}
               ></div>
            ))}
         </div>

      </div>
      
      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded border border-slate-700">
         <span>Single Event Upsets: <span className="text-red-400 font-bold">Detected</span></span>
         <span>ECC Corrections: <span className="text-emerald-400 font-bold">{fixedCount}</span></span>
         <span className="col-span-2 text-purple-400">Background Sweep: <span className="text-white">Continuous</span></span>
      </div>
    </div>
  );
};
