import React, { useState, useEffect } from 'react';

export const HaloMapping: React.FC = () => {
  const [wimpHits, setWimpHits] = useState(0);
  const [density, setDensity] = useState(0.3); // Standard 0.3 GeV/cm3
  const [noiseEvents, setNoiseEvents] = useState(0);

  useEffect(() => {
    // Simulate deep underground Xenon detector
    const detector = setInterval(() => {
       // Huge amount of background radiation (noise)
       setNoiseEvents(prev => prev + Math.floor(Math.random() * 500));
       
       // Extremely rare WIMP dark matter collisions
       if (Math.random() > 0.95) {
          setWimpHits(prev => prev + 1);
          setDensity(prev => prev + (Math.random() * 0.05));
       }
    }, 100);

    return () => clearInterval(detector);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-indigo-400">Dark Matter</h2>
          <p className="text-xs text-slate-400">Halo Gravimeter (LZ TPC)</p>
        </div>
        <div className="px-2 py-1 rounded text-[10px] font-mono border bg-slate-800 text-slate-400 border-slate-700">
          2KM UNDERGROUND
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex items-center justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* Galactic Rotation curve background */}
         <div className="absolute inset-0 opacity-30 flex items-center justify-center">
            <div className="w-48 h-12 border-b-2 border-indigo-500/50 rounded-[50%]" style={{ transform: 'rotate(-15deg)' }}></div>
         </div>

         {/* Liquid Xenon Tank */}
         <div className="relative w-24 h-32 border-2 border-slate-600 rounded-lg bg-sky-900/20 overflow-hidden shadow-[0_0_20px_rgba(56,189,248,0.1)]">
            {/* Photomultiplier tubes (top/bottom) */}
            <div className="absolute top-0 left-0 right-0 h-4 bg-slate-700 flex justify-around items-center px-1">
               {[...Array(5)].map((_, i) => <div key={i} className="w-2 h-2 rounded-full bg-slate-900"></div>)}
            </div>
            <div className="absolute bottom-0 left-0 right-0 h-4 bg-slate-700 flex justify-around items-center px-1">
               {[...Array(5)].map((_, i) => <div key={i} className="w-2 h-2 rounded-full bg-slate-900"></div>)}
            </div>

            {/* Liquid Xenon Fluid */}
            <div className="absolute top-4 bottom-4 left-0 right-0 bg-gradient-to-b from-sky-400/10 to-sky-600/20"></div>

            {/* Background Noise (Electron Recoils) */}
            {[...Array(10)].map((_, i) => (
               <div 
                  key={`noise-${i}`}
                  className="absolute w-px h-px bg-red-400 shadow-[0_0_2px_#f87171]"
                  style={{ 
                     left: `${Math.random() * 100}%`, 
                     top: `${20 + Math.random() * 60}%`,
                     opacity: Math.random(),
                     animation: 'ping 0.5s cubic-bezier(0, 0, 0.2, 1) infinite',
                     animationDelay: `${Math.random()}s`
                  }}
               ></div>
            ))}

            {/* Rare WIMP hit (Nuclear Recoil) */}
            <div 
               className="absolute w-2 h-2 bg-indigo-400 rounded-full shadow-[0_0_15px_#818cf8]"
               style={{ 
                  left: '50%', 
                  top: '50%',
                  transform: 'translate(-50%, -50%)',
                  opacity: wimpHits % 2 === 0 ? 0 : 1, // Flash on hit
                  transition: 'opacity 0.1s'
               }}
            ></div>
         </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Local DM Density</div>
            <div className="text-lg font-mono font-bold text-indigo-400">
               {density.toFixed(2)} <span className="text-xs text-slate-500">GeV/cm³</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">WIMP Detections</div>
            <div className="text-lg font-mono font-bold text-white">
               {wimpHits} <span className="text-[8px] text-red-400">/ {noiseEvents > 1000 ? (noiseEvents/1000).toFixed(1) + 'k' : noiseEvents} noise</span>
            </div>
         </div>
      </div>

      <div className="grid grid-cols-1 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded text-center">
         <span>Galactic Rotation: <span className="text-emerald-400">STABLE (Flat Curve)</span></span>
      </div>
    </div>
  );
};
