import React, { useState, useEffect } from 'react';

export const DysonMegastructure: React.FC = () => {
  const [capturePercent, setCapturePercent] = useState(0);
  const [powerGenerated, setPowerGenerated] = useState(0); // Yottawatts
  const [homeworldAlert, setHomeworldAlert] = useState(false);

  useEffect(() => {
    // Simulate Megastructure Construction
    const builder = setInterval(() => {
       if (capturePercent < 100) {
          setCapturePercent(prev => {
             const next = prev + 0.5;
             if (next > 25 && next < 99) setHomeworldAlert(true); // Artificial condition for demo: homeworld not relocated yet
             else setHomeworldAlert(false);
             return Math.min(100, next);
          });
          
          // Our sun outputs 384.6 Yottawatts total
          setPowerGenerated((capturePercent / 100) * 384.6);
       }
    }, 200);

    return () => clearInterval(builder);
  }, [capturePercent]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-yellow-500">Megastructure</h2>
          <p className="text-xs text-slate-400">Dyson Swarm Architect</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-bold border ${capturePercent >= 100 ? 'bg-yellow-900/50 text-yellow-400 border-yellow-600' : 'bg-slate-800 text-slate-400 border-slate-700'}`}>
          {capturePercent >= 100 ? 'TYPE II CIVILIZATION' : 'CONSTRUCTING'}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex items-center justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)] perspective-[600px]">
         
         {/* The Star */}
         <div className="absolute w-24 h-24 rounded-full bg-yellow-400 shadow-[0_0_60px_#eab308] transition-opacity duration-300" style={{ opacity: 1 - (capturePercent / 100) }}></div>
         
         {/* The Dyson Swarm (Rings of satellites) */}
         <div className="absolute inset-0 flex items-center justify-center" style={{ transformStyle: 'preserve-3d', transform: 'rotateX(60deg) rotateZ(20deg)' }}>
            
            {/* Ring 1 (Inner) */}
            <div className="absolute w-32 h-32 border-[8px] border-dashed border-slate-500/50 rounded-full animate-[spin_10s_linear_infinite]" style={{ opacity: capturePercent > 10 ? 1 : capturePercent/10 }}></div>
            
            {/* Ring 2 (Middle, perpendicular) */}
            <div className="absolute w-40 h-40 border-[12px] border-dashed border-slate-600/70 rounded-full animate-[spin_15s_linear_infinite_reverse]" style={{ transform: 'rotateY(90deg)', opacity: capturePercent > 40 ? 1 : Math.max(0, (capturePercent-10)/30) }}></div>
            
            {/* Shell completion (Outer shell blocking light) */}
            {capturePercent > 80 && (
               <div className="absolute w-48 h-48 rounded-full bg-slate-900/90 shadow-[inset_0_0_50px_rgba(0,0,0,0.9)]" style={{ opacity: (capturePercent-80)/20, transform: 'rotateX(-60deg) rotateZ(-20deg)' }}>
                  {/* Glowing seams */}
                  <div className="w-full h-full rounded-full border border-yellow-500/30 shadow-[0_0_10px_#eab308]"></div>
               </div>
            )}
         </div>

         {/* Energy Beaming to Homeworld (Microwave lasers) */}
         {capturePercent > 0 && capturePercent < 100 && (
            <div className="absolute right-0 top-1/2 w-1/2 h-px bg-yellow-300/50 shadow-[0_0_5px_#fde047] animate-pulse" style={{ transformOrigin: 'left', transform: 'rotate(15deg)' }}></div>
         )}
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Stellar Encapsulation</div>
            <div className={`text-lg font-mono font-bold ${capturePercent >= 100 ? 'text-yellow-400' : 'text-slate-300'}`}>
               {capturePercent.toFixed(1)} <span className="text-xs text-slate-500">%</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Power Output</div>
            <div className="text-lg font-mono font-bold text-yellow-400">
               {powerGenerated.toFixed(1)} <span className="text-xs">YW</span>
            </div>
         </div>
      </div>

      <div className="w-full bg-slate-950 rounded border border-slate-800 p-2 text-[10px] font-mono text-center">
         <span className={homeworldAlert ? 'text-red-400' : 'text-emerald-400'}>
            {homeworldAlert ? 'ECOLOGICAL WARNING: HOMEWORLD FREEZING' : (capturePercent >= 100 ? 'TOTAL SYSTEM POWER ACQUIRED' : 'SWARM ASSEMBLY NOMINAL')}
         </span>
      </div>
    </div>
  );
};
