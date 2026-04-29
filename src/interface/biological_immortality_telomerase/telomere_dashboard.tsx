import React, { useState, useEffect } from 'react';

export const TelomereDashboard: React.FC = () => {
  const [basePairs, setBasePairs] = useState(8000); // Standard length
  const [therapyActive, setTherapyActive] = useState(false);
  const [cellDivisions, setCellDivisions] = useState(0);

  useEffect(() => {
    // Simulate biological aging vs. rejuvenation
    const cellularClock = setInterval(() => {
       setCellDivisions(prev => prev + 1);
       
       setBasePairs(prev => {
          if (therapyActive) {
             // TERT enzyme actively repairing and lengthening telomeres
             return Math.min(15000, prev + 15);
          } else {
             // Normal aging: losing 50-100 base pairs per division
             return Math.max(0, prev - 25);
          }
       });
    }, 200);

    return () => clearInterval(cellularClock);
  }, [therapyActive]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-emerald-400">Telomerase Therapy</h2>
          <p className="text-xs text-slate-400">Biological Immortality Vector</p>
        </div>
        <button 
           onClick={() => setTherapyActive(!therapyActive)}
           className={`px-3 py-1 font-bold text-[10px] rounded border transition-colors ${therapyActive ? 'bg-emerald-600 text-white border-emerald-400 shadow-[0_0_10px_#10b981]' : 'bg-slate-800 text-slate-400 border-slate-600'}`}
        >
           {therapyActive ? 'REJUVENATING' : 'NORMAL AGING'}
        </button>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex flex-col items-center justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* DNA Double Helix Representation */}
         <div className="relative w-full h-12 flex items-center justify-center">
            {[...Array(15)].map((_, i) => {
               // Sine wave calculation for helix
               const phase = (i / 15) * Math.PI * 4;
               const y1 = Math.sin(phase) * 15;
               const y2 = Math.sin(phase + Math.PI) * 15;
               
               return (
                  <div key={i} className="absolute w-full h-full flex justify-center" style={{ left: `${(i/15)*100 - 50}%` }}>
                     <div className="w-1 h-1 bg-slate-500 rounded-full absolute" style={{ top: `calc(50% + ${y1}px)` }}></div>
                     <div className="w-1 h-1 bg-slate-500 rounded-full absolute" style={{ top: `calc(50% + ${y2}px)` }}></div>
                     <div className="w-px bg-slate-700 absolute" style={{ top: `calc(50% + ${Math.min(y1, y2)}px)`, height: Math.abs(y1 - y2) }}></div>
                  </div>
               )
            })}
         </div>

         {/* The Telomere Cap (Changes length and color) */}
         <div className="mt-8 relative w-full h-6 bg-slate-800 rounded-full border border-slate-700 overflow-hidden">
            {/* Critical Senescence Zone */}
            <div className="absolute top-0 bottom-0 left-0 w-[20%] bg-red-900/30 border-r border-red-500/50"></div>
            
            {/* Actual Telomere Length */}
            <div 
               className={`absolute top-0 bottom-0 left-0 transition-all duration-300 ${basePairs < 3000 ? 'bg-red-500 animate-pulse' : therapyActive ? 'bg-emerald-500' : 'bg-sky-500'}`}
               style={{ width: `${(basePairs / 15000) * 100}%` }}
            >
               {/* TERT Enzyme injection visual */}
               {therapyActive && (
                  <div className="absolute top-0 bottom-0 right-0 w-8 bg-white/50 blur-sm animate-[pulse_0.2s_linear_infinite]"></div>
               )}
            </div>
         </div>
         <div className="text-[10px] text-slate-500 font-mono mt-1 w-full text-center">Chromosome Terminus (TTAGGG)ₙ</div>

      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Base Pairs</div>
            <div className={`text-lg font-mono font-bold ${basePairs < 3000 ? 'text-red-400' : 'text-emerald-400'}`}>
               {basePairs.toLocaleString()} <span className="text-xs">bp</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Mitotic Divisions</div>
            <div className="text-lg font-mono font-bold text-white">
               {cellDivisions.toLocaleString()}
            </div>
         </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded text-center">
         <span className={basePairs < 3000 ? 'text-red-400 animate-pulse' : 'text-slate-400'}>Status: {basePairs < 3000 ? 'SENESCENCE (DEATH)' : 'HEALTHY'}</span>
         <span>Vector: <span className="text-emerald-400">Lipid Nanoparticle</span></span>
      </div>
    </div>
  );
};
