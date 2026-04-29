import React, { useState, useEffect } from 'react';

export const ContainmentMonitor: React.FC = () => {
  const [cloudRadius, setCloudRadius] = useState(20);
  const [vacuumTorr, setVacuumTorr] = useState(1e-12);
  const [isStable, setIsStable] = useState(true);

  useEffect(() => {
    const dynamics = setInterval(() => {
      // Cloud naturally expands due to Coulomb repulsion, RF cooling pushes it back
      setCloudRadius(prev => {
         const next = prev + (Math.random() - 0.4) * 2;
         return Math.max(10, Math.min(40, next));
      });

      // Vacuum fluctuations
      setVacuumTorr(prev => {
         const noise = prev * (Math.random() * 0.1);
         return prev + noise;
      });
    }, 100);

    return () => clearInterval(dynamics);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-fuchsia-500">Penning Trap</h2>
          <p className="text-xs text-slate-400">Antimatter Containment</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-mono border ${isStable ? 'bg-fuchsia-900/30 text-fuchsia-400 border-fuchsia-800' : 'bg-red-900/50 text-red-400 border-red-800 animate-pulse'}`}>
          {isStable ? 'MAGNETIC BOTTLE ACTIVE' : 'CONTAINMENT BREACH'}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[180px] flex items-center justify-center relative overflow-hidden">
         {/* Trap Electrodes (Hyperbolic shapes) */}
         <div className="absolute top-0 w-32 h-10 border-b-4 border-slate-600 rounded-[50%]"></div>
         <div className="absolute bottom-0 w-32 h-10 border-t-4 border-slate-600 rounded-[50%]"></div>
         <div className="absolute left-0 w-10 h-full border-r-4 border-slate-600 rounded-[50%]"></div>
         <div className="absolute right-0 w-10 h-full border-l-4 border-slate-600 rounded-[50%]"></div>

         {/* Magnetic Field Lines */}
         <div className="absolute inset-0 flex justify-between px-10 opacity-20">
            {[...Array(5)].map((_, i) => <div key={i} className="h-full w-px bg-cyan-400"></div>)}
         </div>

         {/* The Antimatter Cloud (Positrons) */}
         <div 
            className="rounded-full bg-fuchsia-500 blur-md relative flex items-center justify-center transition-all duration-75"
            style={{ 
               width: `${cloudRadius * 2}px`, 
               height: `${cloudRadius * 2}px`,
               boxShadow: `0 0 30px #d946ef`
            }}
         >
            <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
         </div>
      </div>
      
      <div className="space-y-2 mb-4">
         <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400">Vacuum Pressure</span>
            <span className="font-bold font-mono text-emerald-400">{vacuumTorr.toExponential(2)} Torr</span>
         </div>
         <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400">Particles Contained</span>
            <span className="font-bold font-mono text-fuchsia-400">1.2 × 10^7 e+</span>
         </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>B-Field: <span className="text-white">5.0 Tesla</span></span>
         <span>Cooling: <span className="text-sky-400">4.2 Kelvin</span></span>
      </div>
    </div>
  );
};
