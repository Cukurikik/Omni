import React, { useState, useEffect } from 'react';

export const TypeIvGrid: React.FC = () => {
  const [harvestingVolume, setHarvestingVolume] = useState(1); // Billion cubic LY
  const [energyHarvested, setEnergyHarvested] = useState(0);
  const [entropyRate, setEntropyRate] = useState(100);
  const [heatDeathReversed, setHeatDeathReversed] = useState(false);

  useEffect(() => {
    const grid = setInterval(() => {
       // Harvest dark energy based on volume
       const energy = harvestingVolume * 5.4; // Scaled for UI
       setEnergyHarvested(energy);
       
       // Reduce entropy
       setEntropyRate(prev => {
          const next = prev - (energy * 0.5) + 10; // Natural increase vs harvesting
          if (next <= 0) {
             setHeatDeathReversed(true);
             return 0;
          }
          setHeatDeathReversed(false);
          return next;
       });
    }, 500);

    return () => clearInterval(grid);
  }, [harvestingVolume]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-fuchsia-400">Type IV Omni Grid</h2>
          <p className="text-xs text-slate-400">Dark Energy Extraction</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-bold border ${heatDeathReversed ? 'bg-emerald-900/50 text-emerald-400 border-emerald-500 shadow-[0_0_15px_#10b981]' : 'bg-slate-800 text-fuchsia-400 border-slate-700'}`}>
          {heatDeathReversed ? 'NEGUENTROPY ATTAINED' : 'FIGHTING HEAT DEATH'}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex items-center justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* The Cosmic Web (Galaxy Superclusters) */}
         <div className="absolute inset-0 opacity-40">
            <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
               <path d="M10,10 Q30,40 50,20 T90,10 M20,80 Q40,50 60,70 T90,80 M10,50 Q30,30 50,50 T90,50" fill="none" stroke="#a855f7" strokeWidth="0.5" className="animate-pulse"/>
               {/* Nodes (Galaxies) */}
               <circle cx="10" cy="10" r="1" fill="#fff" />
               <circle cx="50" cy="20" r="1.5" fill="#fff" />
               <circle cx="90" cy="10" r="1" fill="#fff" />
               <circle cx="20" cy="80" r="1.2" fill="#fff" />
               <circle cx="60" cy="70" r="1" fill="#fff" />
               <circle cx="90" cy="80" r="1.5" fill="#fff" />
               <circle cx="10" cy="50" r="1" fill="#fff" />
               <circle cx="50" cy="50" r="2" fill="#fff" className="shadow-[0_0_10px_#fff]" />
               <circle cx="90" cy="50" r="1" fill="#fff" />
            </svg>
         </div>

         {/* Intergalactic Void Harvesters (Inverting Cosmological Constant) */}
         <div 
            className="absolute flex items-center justify-center transition-all duration-300"
            style={{
               width: `${Math.min(100, harvestingVolume * 10)}%`,
               height: `${Math.min(100, harvestingVolume * 10)}%`,
            }}
         >
            {/* The inverted vacuum */}
            <div className={`w-full h-full rounded-full blur-xl mix-blend-screen transition-colors ${heatDeathReversed ? 'bg-emerald-500/30' : 'bg-fuchsia-600/30'}`}></div>
            
            {/* Extraction Beams to center */}
            <div className="absolute inset-0">
               <div className="absolute top-0 left-1/2 w-px h-1/2 bg-gradient-to-b from-fuchsia-400 to-transparent"></div>
               <div className="absolute bottom-0 left-1/2 w-px h-1/2 bg-gradient-to-t from-fuchsia-400 to-transparent"></div>
               <div className="absolute left-0 top-1/2 h-px w-1/2 bg-gradient-to-r from-fuchsia-400 to-transparent"></div>
               <div className="absolute right-0 top-1/2 h-px w-1/2 bg-gradient-to-l from-fuchsia-400 to-transparent"></div>
            </div>
         </div>
         
         {/* Central Processor */}
         <div className={`absolute w-4 h-4 rounded-full ${heatDeathReversed ? 'bg-emerald-400 shadow-[0_0_20px_#34d399]' : 'bg-white shadow-[0_0_15px_#fff]'} z-10 animate-pulse`}></div>
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Harvesting Vol</div>
            <div className="text-lg font-mono font-bold text-slate-300">
               {harvestingVolume.toFixed(1)} <span className="text-xs text-slate-500">B cLY</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Universal Entropy Rate</div>
            <div className={`text-lg font-mono font-bold ${heatDeathReversed ? 'text-emerald-400' : 'text-orange-400'}`}>
               {entropyRate.toFixed(1)} <span className="text-xs text-slate-500">dS/dt</span>
            </div>
         </div>
      </div>

      <div className="w-full bg-slate-950 rounded border border-slate-800 p-2 flex flex-col gap-2">
         <div className="flex justify-between items-center">
            <span className="text-[10px] font-mono text-slate-500">Void Deployment</span>
            <input 
               type="range" min="1" max="20" step="1" value={harvestingVolume} 
               onChange={(e) => setHarvestingVolume(parseFloat(e.target.value))}
               className="w-1/2 accent-fuchsia-500"
            />
         </div>
         <div className="text-xs font-mono text-center mt-1">
            <span className={heatDeathReversed ? 'text-emerald-400 font-bold' : 'text-slate-400'}>
               {heatDeathReversed ? 'UNIVERSE SAVED FROM THERMAL EQUILIBRIUM' : 'EXTRACTING DARK ENERGY FROM THE VOID'}
            </span>
         </div>
      </div>
    </div>
  );
};
