import React, { useState, useEffect } from 'react';

export const ShkadovThruster: React.FC = () => {
  const [thrustActive, setThrustActive] = useState(true);
  const [distanceMoved, setDistanceMoved] = useState(0); // Lightyears
  const [yearsElapsed, setYearsElapsed] = useState(0); // Millions of years
  const [hazardDistance, setHazardDistance] = useState(15); // Lightyears to supernova

  useEffect(() => {
    // Simulate millions of years of travel
    const astrogation = setInterval(() => {
       if (thrustActive) {
          setYearsElapsed(prev => prev + 0.1); // 100k years per tick
          
          // Acceleration means distance increases exponentially over time, but for UI we simplify
          setDistanceMoved(prev => {
             const newDist = prev + (yearsElapsed * 0.05);
             return newDist;
          });
       }
    }, 100);

    return () => clearInterval(astrogation);
  }, [thrustActive, yearsElapsed]);

  const hazardCleared = distanceMoved > hazardDistance;

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-amber-500">Stellar Engine</h2>
          <p className="text-xs text-slate-400">Class-A Shkadov Thruster</p>
        </div>
        <button 
           onClick={() => setThrustActive(!thrustActive)}
           className={`px-3 py-1 font-bold text-[10px] rounded border transition-colors ${thrustActive ? 'bg-amber-900/50 text-amber-400 border-amber-600' : 'bg-slate-800 text-slate-400 border-slate-600'}`}
        >
           {thrustActive ? 'ENGINE FIRING' : 'ENGINE HALTED'}
        </button>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* Galactic Background */}
         <div className="absolute inset-0 opacity-20" style={{ background: 'radial-gradient(circle at right, #4c1d95 0%, transparent 70%)' }}></div>

         {/* The Supernova Hazard */}
         <div className="absolute right-4 top-1/2 -translate-y-1/2 flex flex-col items-center">
            <div className={`w-8 h-8 rounded-full bg-red-500 shadow-[0_0_30px_#ef4444] ${!hazardCleared ? 'animate-pulse' : 'opacity-50'}`}></div>
            <span className="text-[8px] text-red-400 mt-2">HAZARD (SN)</span>
         </div>

         {/* The Moving Solar System */}
         <div 
            className="absolute top-1/2 -translate-y-1/2 transition-all duration-100"
            style={{ 
               left: `calc(20% + ${(distanceMoved / 30) * 100}%)`, // Move across screen based on distance
            }}
         >
            {/* The Shkadov Mirror (Semi-circle blocking/reflecting light) */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-16 h-16 border-l-[8px] border-slate-300 rounded-full shadow-[inset_4px_0_10px_rgba(253,224,71,0.5)]"></div>
            
            {/* The Star */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-6 h-6 rounded-full bg-yellow-400 shadow-[0_0_20px_#eab308]"></div>
            
            {/* Radiation Pressure / Thrust exhaust */}
            {thrustActive && (
               <div className="absolute top-1/2 right-4 -translate-y-1/2 w-24 h-12 bg-gradient-to-r from-yellow-400/40 to-transparent blur-md"></div>
            )}
         </div>

         {/* Safety Distance Line */}
         <div className="absolute top-0 bottom-0 border-l border-dashed border-emerald-500/50" style={{ left: `calc(20% + ${(hazardDistance / 30) * 100}%)` }}>
            <span className="absolute bottom-2 left-2 text-[8px] text-emerald-400">SAFE ZONE</span>
         </div>
      </div>
      
      <div className="grid grid-cols-3 gap-2 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800 flex flex-col items-center">
            <div className="text-[9px] uppercase text-slate-500 mb-1">Time Elapsed</div>
            <div className="text-sm font-mono font-bold text-slate-300">
               {yearsElapsed.toFixed(1)}<span className="text-[10px] text-slate-500">M yr</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800 flex flex-col items-center">
            <div className="text-[9px] uppercase text-slate-500 mb-1">Dist Moved</div>
            <div className={`text-sm font-mono font-bold ${hazardCleared ? 'text-emerald-400' : 'text-amber-400'}`}>
               {distanceMoved.toFixed(1)}<span className="text-[10px] text-slate-500">LY</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800 flex flex-col items-center">
            <div className="text-[9px] uppercase text-slate-500 mb-1">Thrust</div>
            <div className={`text-sm font-mono font-bold ${thrustActive ? 'text-white' : 'text-slate-600'}`}>
               {thrustActive ? '3.5e18' : '0.0'}<span className="text-[10px] text-slate-500">N</span>
            </div>
         </div>
      </div>

      <div className="w-full bg-slate-950 rounded border border-slate-800 p-2 text-xs font-mono text-center">
         <span className={hazardCleared ? 'text-emerald-400' : 'text-red-400 animate-pulse'}>
            {hazardCleared ? 'HAZARD EVADED - TRAJECTORY SAFE' : 'WARNING: SYSTEM IN BLAST RADIUS'}
         </span>
      </div>
    </div>
  );
};
