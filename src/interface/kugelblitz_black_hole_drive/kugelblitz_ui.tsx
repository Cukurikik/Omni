import React, { useState, useEffect } from 'react';

export const KugelblitzUi: React.FC = () => {
  const [energyInjection, setEnergyInjection] = useState(0); // Yottawatts
  const [horizonRadius, setHorizonRadius] = useState(0); // Attometers
  const [driveActive, setDriveActive] = useState(false);
  const [acceleration, setAcceleration] = useState(0); // Gs

  useEffect(() => {
    let loop: NodeJS.Timeout;
    
    if (driveActive) {
       // Spooling up the laser array
       loop = setInterval(() => {
          setEnergyInjection(prev => {
             const next = Math.min(500, prev + 10);
             
             // If enough energy is injected, spacetime collapses into a Kugelblitz
             if (next > 400) {
                setHorizonRadius(1.5); // Attometers
                setAcceleration(prevA => Math.min(85, prevA + 2)); // Massive thrust
             }
             
             return next;
          });
       }, 100);
    } else {
       // Spooling down / Evaporating
       loop = setInterval(() => {
          setEnergyInjection(prev => Math.max(0, prev - 20));
          setHorizonRadius(0); // Instant evaporation when lasers cut
          setAcceleration(prev => Math.max(0, prev - 5));
       }, 100);
    }

    return () => clearInterval(loop);
  }, [driveActive]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-violet-500">Kugelblitz Drive</h2>
          <p className="text-xs text-slate-400">Energy-Singularity Engine</p>
        </div>
        <button 
           onClick={() => setDriveActive(!driveActive)}
           className={`px-3 py-1 font-bold text-[10px] rounded border transition-colors ${driveActive ? 'bg-violet-600 text-white border-violet-400 shadow-[0_0_15px_#8b5cf6]' : 'bg-slate-800 text-slate-400 border-slate-600'}`}
        >
           {driveActive ? 'SCRAM DRIVE' : 'IGNITE LASERS'}
        </button>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex flex-col items-center justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* Incoming Laser Arrays (Dyson Swarm Focus) */}
         {energyInjection > 0 && (
            <div className="absolute inset-0 flex items-center justify-center">
               {[...Array(12)].map((_, i) => (
                  <div 
                     key={i} 
                     className="absolute w-full h-[2px] bg-sky-400 mix-blend-screen" 
                     style={{ 
                        transform: `rotate(${i * 15}deg)`,
                        opacity: energyInjection / 500,
                        boxShadow: `0 0 ${energyInjection / 20}px #38bdf8`
                     }}
                  ></div>
               ))}
            </div>
         )}

         {/* The Focal Point / Kugelblitz */}
         <div className="relative z-10 w-16 h-16 flex items-center justify-center">
            {horizonRadius > 0 ? (
               // Active Black Hole
               <div className="relative flex items-center justify-center">
                  <div className="w-20 h-20 rounded-full border-4 border-violet-500/50 bg-violet-900/20 blur-md animate-pulse"></div>
                  <div className="absolute w-8 h-8 bg-black rounded-full shadow-[0_0_30px_#8b5cf6]"></div>
                  {/* Gamma Ray Exhaust thrusting backwards */}
                  <div className="absolute top-full w-4 h-32 bg-gradient-to-b from-white via-violet-400 to-transparent blur-sm"></div>
               </div>
            ) : (
               // Spooling / Empty
               <div className="w-2 h-2 bg-white rounded-full transition-all" style={{ transform: `scale(${energyInjection / 100})`, opacity: energyInjection > 0 ? 1 : 0.2, boxShadow: `0 0 ${energyInjection/10}px #fff` }}></div>
            )}
         </div>

         {/* Thrust Vectors */}
         {acceleration > 0 && (
            <div className="absolute bottom-4 right-4 text-[10px] font-mono text-violet-300 animate-pulse">
               EXHAUST V: 1.0c
            </div>
         )}
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Laser Feed</div>
            <div className={`text-lg font-mono font-bold ${energyInjection > 400 ? 'text-sky-400' : 'text-slate-400'}`}>
               {energyInjection.toFixed(0)} <span className="text-xs">YW</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800 relative overflow-hidden">
            <div className="text-[10px] uppercase text-slate-500 mb-1 relative z-10">Acceleration</div>
            <div className={`text-lg font-mono font-bold relative z-10 ${acceleration > 80 ? 'text-violet-400' : 'text-white'}`}>
               {acceleration.toFixed(1)} <span className="text-xs">G</span>
            </div>
            <div className="absolute bottom-0 left-0 bg-violet-900/40 w-full" style={{ height: `${(acceleration / 100) * 100}%` }}></div>
         </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Horizon: <span className={horizonRadius > 0 ? 'text-emerald-400' : 'text-slate-500'}>{horizonRadius.toFixed(1)} am</span></span>
         <span>Fuel: <span className="text-white">Pure Light</span></span>
      </div>
    </div>
  );
};
