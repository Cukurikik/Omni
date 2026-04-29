import React, { useState, useEffect } from 'react';

export const BraneCosmology: React.FC = () => {
  const [distance, setDistance] = useState(10); // Distance in 5th dimension (Planck lengths)
  const [collisionWarning, setCollisionWarning] = useState(false);
  const [energy, setEnergy] = useState(0);

  useEffect(() => {
    // Simulate Ekpyrotic approach
    const approach = setInterval(() => {
       setDistance(prev => {
          if (prev <= 0) {
             setCollisionWarning(true);
             return 0;
          }
          return prev - 0.1;
       });
       
       if (distance > 0 && distance < 2) {
          setEnergy(Math.pow((2 - distance) * 10, 2));
       } else if (distance <= 0) {
          setEnergy(1000); // Big Bang triggered
       }
    }, 100);

    return () => clearInterval(approach);
  }, [distance]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-fuchsia-500">M-Theory Bulk</h2>
          <p className="text-xs text-slate-400">Ekpyrotic Brane Collision</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-mono border ${collisionWarning ? 'bg-fuchsia-900/50 text-fuchsia-400 border-fuchsia-800 animate-pulse' : 'bg-slate-800 text-slate-400 border-slate-700'}`}>
          {collisionWarning ? 'BIG BANG INITIATED' : 'GRAVITON ANOMALY'}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex flex-col items-center justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* Higher Dimensional Bulk Background */}
         <div className="absolute inset-0 opacity-20 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-fuchsia-900 via-transparent to-transparent"></div>

         {/* Our Brane (Universe) */}
         <div className="w-full h-8 bg-blue-500/20 border-t border-b border-blue-400 rounded-lg absolute shadow-[0_0_15px_#3b82f6]" style={{ bottom: '20%' }}>
            <div className="text-[8px] text-blue-300 ml-2 mt-1 font-mono">LOCAL BRANE (3D)</div>
         </div>

         {/* Approaching Shadow Brane */}
         <div 
            className="w-full h-8 bg-fuchsia-500/20 border-t border-b border-fuchsia-400 rounded-lg absolute shadow-[0_0_15px_#d946ef] transition-all duration-75" 
            style={{ bottom: `${20 + distance * 5}%` }}
         >
            <div className="text-[8px] text-fuchsia-300 ml-2 mt-1 font-mono">SHADOW BRANE</div>
         </div>

         {/* Graviton leakage between branes */}
         {distance > 0 && distance < 8 && (
            <div className="absolute inset-x-0 flex justify-around" style={{ bottom: '30%', top: `${100 - (20 + distance * 5)}%` }}>
               {[...Array(5)].map((_, i) => (
                  <div key={i} className="w-px bg-white/50 h-full animate-pulse" style={{ animationDelay: `${i * 0.1}s` }}></div>
               ))}
            </div>
         )}
         
         {/* Collision Flash */}
         {collisionWarning && (
            <div className="absolute inset-0 bg-white z-10 animate-[ping_2s_ease-out_forwards]"></div>
         )}
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">5D Distance</div>
            <div className={`text-lg font-mono font-bold ${distance < 2 ? 'text-red-400 animate-pulse' : 'text-fuchsia-400'}`}>
               {distance.toFixed(2)} <span className="text-xs">Lₚ</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Vacuum State</div>
            <div className="text-lg font-mono font-bold text-emerald-400">
               {collisionWarning ? 'DECAYING' : 'METASTABLE'}
            </div>
         </div>
      </div>

      <div className="grid grid-cols-1 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded text-center">
         <span>Collision Energy: <span className="text-white">{energy.toFixed(0)} GeV³</span></span>
      </div>
    </div>
  );
};
