import React, { useState, useEffect } from 'react';

export const StarEvolution: React.FC = () => {
  const [ageMyr, setAgeMyr] = useState(0);
  const [coreElement, setCoreElement] = useState('Hydrogen');
  const [coreMass, setCoreMass] = useState(0.8); // Solar masses
  const [isSupernova, setIsSupernova] = useState(false);

  useEffect(() => {
    // Simulate stellar life cycle of a massive star (20 Solar Masses)
    // They burn fast and die young (approx 10 million years)
    const evolution = setInterval(() => {
      setAgeMyr(prev => {
         const next = prev + 0.5;
         
         if (next > 10.5) setIsSupernova(true);
         else if (next > 10.0) { setCoreElement('Iron'); setCoreMass(1.45); } // Exceeds Chandrasekhar limit
         else if (next > 9.0) setCoreElement('Silicon');
         else if (next > 8.0) setCoreElement('Oxygen');
         else if (next > 5.0) setCoreElement('Carbon');
         else if (next > 2.0) setCoreElement('Helium');
         
         return next;
      });
      
    }, 500);

    return () => clearInterval(evolution);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-orange-500">Stellar Evolution</h2>
          <p className="text-xs text-slate-400">Nucleosynthesis Simulator</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-mono border ${isSupernova ? 'bg-white text-black border-white animate-pulse' : 'bg-orange-900/30 text-orange-400 border-orange-800'}`}>
          {isSupernova ? 'SUPERNOVA SHOCKWAVE' : 'FUSING CORE'}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[180px] flex items-center justify-center relative overflow-hidden">
         
         {!isSupernova ? (
            // Onion-like shell burning structure
            <div className="relative flex items-center justify-center w-full h-full">
               <div className="absolute w-32 h-32 rounded-full border border-orange-500/30 bg-red-900/20"></div> {/* H */}
               <div className="absolute w-24 h-24 rounded-full border border-yellow-500/50 bg-orange-900/40"></div> {/* He */}
               <div className="absolute w-16 h-16 rounded-full border border-yellow-300/80 bg-yellow-700/60"></div> {/* C/O */}
               <div className="absolute w-8 h-8 rounded-full border border-white bg-slate-300 shadow-[0_0_20px_#fff] flex items-center justify-center text-[8px] text-black font-bold">
                  {coreElement.substring(0,2).toUpperCase()}
               </div>
            </div>
         ) : (
            // Supernova Explosion
            <div className="relative flex items-center justify-center w-full h-full">
               {/* Remnant (Neutron Star/Black Hole) */}
               <div className="w-2 h-2 bg-black rounded-full shadow-[0_0_10px_#fff] z-20 border border-white/50"></div>
               
               {/* Expanding Shockwave */}
               <div className="absolute w-full h-full rounded-full border-4 border-white opacity-80 animate-[ping_1s_ease-out_forwards]"></div>
               <div className="absolute w-3/4 h-3/4 rounded-full border-[10px] border-cyan-400 opacity-50 blur-md animate-[ping_2s_ease-out_forwards]"></div>
               <div className="absolute w-1/2 h-1/2 rounded-full bg-orange-500 blur-xl opacity-80 animate-[ping_3s_ease-out_forwards]"></div>
            </div>
         )}

      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Age</div>
            <div className="text-lg font-mono font-bold text-sky-400">{ageMyr.toFixed(1)} <span className="text-xs">Myr</span></div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Core Mass</div>
            <div className={`text-lg font-mono font-bold ${coreMass >= 1.44 ? 'text-red-400' : 'text-orange-400'}`}>
               {coreMass.toFixed(2)} <span className="text-xs">M☉</span>
            </div>
         </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded text-center">
         <span className="col-span-2">Reaction: <span className="text-emerald-400 text-sm font-bold ml-2">{coreElement} Fusion</span></span>
      </div>
    </div>
  );
};
