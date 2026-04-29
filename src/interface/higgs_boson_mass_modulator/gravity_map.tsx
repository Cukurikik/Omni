import React, { useState, useEffect } from 'react';

export const GravityMap: React.FC = () => {
  const [energyTev, setEnergyTev] = useState(0);
  const [vev, setVev] = useState(246); // Standard Model VEV in GeV
  const [massRatio, setMassRatio] = useState(1.0);
  const [active, setActive] = useState(false);

  useEffect(() => {
    // Simulate Higgs field modulation (Inertial Dampening spool-up)
    if (active) {
       const ramp = setInterval(() => {
          setEnergyTev(prev => Math.min(13.6, prev + 0.5)); // LHC max energy
       }, 100);
       return () => clearInterval(ramp);
    } else {
       const decay = setInterval(() => {
          setEnergyTev(prev => Math.max(0, prev - 1.0));
       }, 100);
       return () => clearInterval(decay);
    }
  }, [active]);

  useEffect(() => {
     // Modulate VEV based on localized energy injection
     // Mock relationship: High TeV energy suppresses the 246 GeV field
     const newVev = 246 * Math.exp(-energyTev / 5);
     setVev(newVev);
     
     // Local mass scales with VEV
     setMassRatio(newVev / 246);
  }, [energyTev]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-amber-500">Higgs Modulator</h2>
          <p className="text-xs text-slate-400">Inertial Dampening Field</p>
        </div>
        <button 
           onClick={() => setActive(!active)}
           className={`px-3 py-1 font-bold text-xs rounded border transition-colors ${active ? 'bg-amber-600 text-white border-amber-400 shadow-[0_0_10px_#d97706]' : 'bg-slate-800 text-slate-400 border-slate-600'}`}
        >
           {active ? 'DAMPEN' : 'ENGAGE'}
        </button>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[180px] flex items-center justify-center relative overflow-hidden">
         
         {/* Spacetime Grid */}
         <div className="absolute inset-0">
            {[...Array(15)].map((_, i) => (
               <div key={`h-${i}`} className="w-full h-px bg-amber-500/10 absolute" style={{ top: `${(i/15)*100}%` }}></div>
            ))}
            {[...Array(15)].map((_, i) => (
               <div key={`v-${i}`} className="h-full w-px bg-amber-500/10 absolute" style={{ left: `${(i/15)*100}%` }}></div>
            ))}
         </div>

         {/* Mexican Hat Potential (Higgs Field Viz) */}
         <div className="relative w-32 h-32 flex items-center justify-center">
            {/* The potential well */}
            <div 
               className="w-full h-full rounded-full border-2 border-amber-500/30 bg-gradient-to-radial from-amber-900/50 to-transparent transition-all duration-500"
               style={{ transform: `scale(${massRatio})` }}
            ></div>
            
            {/* The True Vacuum State (Center) */}
            <div 
               className="absolute rounded-full bg-amber-400 shadow-[0_0_15px_#f59e0b] transition-all duration-500"
               style={{ 
                  width: `${10 + (1-massRatio)*20}px`, 
                  height: `${10 + (1-massRatio)*20}px`,
                  opacity: massRatio
               }}
            ></div>

            {/* High-Energy Particle Collisions */}
            {active && (
               <div className="absolute inset-0 animate-spin" style={{ animationDuration: '0.2s' }}>
                  <div className="w-2 h-2 bg-white rounded-full absolute top-0 left-1/2 shadow-[0_0_10px_#fff]"></div>
                  <div className="w-2 h-2 bg-white rounded-full absolute bottom-0 left-1/2 shadow-[0_0_10px_#fff]"></div>
               </div>
            )}
         </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800 relative overflow-hidden">
            <div className="text-[10px] uppercase text-slate-500 mb-1 relative z-10">Local Higgs VEV</div>
            <div className="text-lg font-mono font-bold text-amber-400 relative z-10">{vev.toFixed(1)} <span className="text-xs">GeV</span></div>
            <div className="absolute bottom-0 left-0 bg-amber-900/30 w-full" style={{ height: `${(vev/246)*100}%` }}></div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Effective Mass</div>
            <div className={`text-lg font-mono font-bold ${massRatio < 0.1 ? 'text-red-400 animate-pulse' : 'text-emerald-400'}`}>
               {(massRatio * 100).toFixed(1)}%
            </div>
         </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded text-center">
         <span>Injection: <span className="text-white">{energyTev.toFixed(1)} TeV</span></span>
         <span>Collision: <span className="text-emerald-400">Gluon-Fusion</span></span>
      </div>
    </div>
  );
};
