import React, { useState, useEffect } from 'react';

export const ZpeYield: React.FC = () => {
  const [distanceNm, setDistanceNm] = useState(15.0);
  const [voltage, setVoltage] = useState(0);
  const [isStiction, setIsStiction] = useState(false);

  useEffect(() => {
    // Simulate Casimir oscillation
    let direction = -1;
    const osc = setInterval(() => {
      setDistanceNm(prev => {
         if (prev <= 5) {
            setIsStiction(true);
            return 5; // Stiction collapse
         }
         if (prev <= 10) direction = 1; // Spring pushes back
         if (prev >= 20) direction = -1; // Casimir pulls in
         
         return prev + direction * 0.5;
      });
      
      // Voltage peaks when plates are closest (highest force)
      if (!isStiction) {
         setVoltage(Math.max(0, (20 - distanceNm) * 1.5 + Math.random() * 2));
      } else {
         setVoltage(0); // System destroyed
      }
    }, 50);

    return () => clearInterval(osc);
  }, [distanceNm, isStiction]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-cyan-400">Casimir Harvester</h2>
          <p className="text-xs text-slate-400">Zero-Point Energy (ZPE)</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-mono border ${isStiction ? 'bg-red-900/50 text-red-400 border-red-800' : 'bg-cyan-900/30 text-cyan-400 border-cyan-800 animate-pulse'}`}>
          {isStiction ? 'STICTION COLLAPSE' : 'HARVESTING VACUUM'}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[180px] flex items-center justify-center relative overflow-hidden">
         
         {/* Quantum Vacuum Fluctuation Background */}
         <div className="absolute inset-0 opacity-30 flex items-center justify-center">
            {[...Array(100)].map((_, i) => (
               <div 
                  key={i} 
                  className="absolute w-1 h-1 bg-white rounded-full animate-ping"
                  style={{
                     top: Math.random() * 100 + '%',
                     left: Math.random() * 100 + '%',
                     animationDuration: (Math.random() * 0.5 + 0.1) + 's'
                  }}
               ></div>
            ))}
         </div>

         {/* Metallic Plates */}
         <div className="flex flex-col items-center justify-center relative z-10 w-full">
            {/* Top Plate (Fixed) */}
            <div className="w-3/4 h-4 bg-slate-400 rounded border-b-2 border-cyan-300 shadow-[0_4px_15px_#22d3ee]"></div>
            
            {/* Vacuum Gap */}
            <div 
               className="w-1/2 flex items-center justify-center border-l border-r border-dashed border-cyan-500/50"
               style={{ height: `${distanceNm * 4}px` }}
            >
               {/* Virtual Particles emerging from nothing */}
               <div className="text-[10px] text-cyan-300/50 font-mono">e+ / e-</div>
            </div>

            {/* Bottom Plate (Piezo Cantilever) */}
            <div className="w-3/4 h-4 bg-slate-400 rounded border-t-2 border-cyan-300 shadow-[0_-4px_15px_#22d3ee]"></div>
         </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4 text-center">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Separation (d)</div>
            <div className={`text-lg font-mono font-bold ${isStiction ? 'text-red-400' : 'text-white'}`}>
               {distanceNm.toFixed(1)} <span className="text-xs">nm</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Piezo Yield</div>
            <div className={`text-lg font-mono font-bold ${isStiction ? 'text-slate-600' : 'text-cyan-400'}`}>
               {voltage.toFixed(1)} <span className="text-xs">mV</span>
            </div>
         </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Force: <span className="text-white">~1/d⁴</span></span>
         <span>Substrate: <span className="text-emerald-400">Graphene</span></span>
      </div>
    </div>
  );
};
