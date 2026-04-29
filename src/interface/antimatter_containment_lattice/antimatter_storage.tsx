import React, { useState, useEffect } from 'react';

export const AntimatterStorage: React.FC = () => {
  const [vacuumTorr, setVacuumTorr] = useState(1e-12);
  const [fieldTesla, setFieldTesla] = useState(5.0);
  const [containmentStatus, setContainmentStatus] = useState<'STABLE' | 'WARNING' | 'BREACH'>('STABLE');

  useEffect(() => {
    // Simulate Penning Trap stability
    const trap = setInterval(() => {
       // Random micro-fluctuations in vacuum and magnets
       if (Math.random() > 0.95) {
          setVacuumTorr(prev => Math.min(1e-8, prev * 10)); // Micro-leak
       } else {
          setVacuumTorr(prev => Math.max(1e-13, prev * 0.5)); // Pumps working
       }
       
       if (Math.random() > 0.98) {
          setFieldTesla(prev => Math.max(0.5, prev - 1.0)); // Magnet glitch
       } else {
          setFieldTesla(prev => Math.min(5.5, prev + 0.1));
       }
    }, 500);

    return () => clearInterval(trap);
  }, []);

  useEffect(() => {
     if (vacuumTorr > 1e-9 || fieldTesla < 2.0) setContainmentStatus('BREACH');
     else if (vacuumTorr > 1e-10 || fieldTesla < 3.5) setContainmentStatus('WARNING');
     else setContainmentStatus('STABLE');
  }, [vacuumTorr, fieldTesla]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-fuchsia-500">Antimatter Cell</h2>
          <p className="text-xs text-slate-400">Penning Trap Lattice</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-bold border ${containmentStatus === 'BREACH' ? 'bg-red-900/80 text-white border-red-500 shadow-[0_0_15px_#ef4444] animate-pulse' : containmentStatus === 'WARNING' ? 'bg-amber-900/50 text-amber-400 border-amber-600' : 'bg-slate-800 text-slate-400 border-slate-700'}`}>
          {containmentStatus}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex flex-col items-center justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* Magnetic Field Lines (Axial) */}
         <div className="absolute inset-0 flex justify-around opacity-40">
            {[...Array(7)].map((_, i) => (
               <div key={i} className={`w-px h-full ${containmentStatus === 'BREACH' ? 'bg-red-500' : 'bg-sky-500'} animate-pulse`} style={{ animationDelay: `${i * 0.1}s` }}></div>
            ))}
         </div>

         {/* Quadrupole Electrodes (Top, Bottom, Ring) */}
         <div className="absolute top-4 w-32 h-8 rounded-[50%] border-4 border-slate-600 bg-slate-800/80 shadow-[0_10px_20px_rgba(0,0,0,0.5)] z-20"></div>
         <div className="absolute bottom-4 w-32 h-8 rounded-[50%] border-4 border-slate-600 bg-slate-800/80 shadow-[0_-10px_20px_rgba(0,0,0,0.5)] z-20"></div>
         
         {/* The Antimatter Cloud (Positrons) */}
         <div className="relative z-10 w-24 h-24 flex items-center justify-center">
            {/* Main containment glow */}
            <div className={`absolute w-full h-full rounded-full blur-md transition-all duration-300 ${containmentStatus === 'BREACH' ? 'bg-red-600/60 scale-150' : containmentStatus === 'WARNING' ? 'bg-amber-500/50 scale-110' : 'bg-fuchsia-600/40'}`}></div>
            
            {/* Core Plasma */}
            <div className="w-12 h-12 rounded-full bg-white shadow-[0_0_30px_#d946ef] flex items-center justify-center overflow-hidden animate-[spin_2s_linear_infinite]">
               {/* Swirling particles */}
               <div className="w-full h-full relative">
                  <div className="absolute top-1 left-2 w-2 h-2 bg-fuchsia-300 rounded-full mix-blend-screen shadow-[0_0_5px_#fff]"></div>
                  <div className="absolute bottom-2 right-1 w-3 h-3 bg-fuchsia-400 rounded-full mix-blend-screen shadow-[0_0_5px_#fff]"></div>
               </div>
            </div>

            {/* Annihilation Flashes (Micro-leaks) */}
            {containmentStatus !== 'STABLE' && (
               <div className="absolute inset-0">
                  <div className="absolute top-0 right-0 w-4 h-4 bg-white rounded-full shadow-[0_0_20px_#fff] animate-ping"></div>
               </div>
            )}
         </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Magnetic Bottle</div>
            <div className={`text-lg font-mono font-bold ${fieldTesla < 3.5 ? 'text-red-400' : 'text-sky-400'}`}>
               {fieldTesla.toFixed(2)} <span className="text-xs">T</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Chamber Vacuum</div>
            <div className={`text-lg font-mono font-bold ${vacuumTorr > 1e-10 ? 'text-amber-400' : 'text-emerald-400'}`}>
               10<sup className="text-xs">{Math.log10(vacuumTorr).toFixed(0)}</sup> <span className="text-xs">Torr</span>
            </div>
         </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded text-center">
         <span>Payload: <span className="text-fuchsia-400">1.5g Positrons</span></span>
         <span>Yield: <span className="text-white">64 Megatons</span></span>
      </div>
    </div>
  );
};
