import React, { useState, useEffect } from 'react';

export const TargetingUi: React.FC = () => {
  const [coherence, setCoherence] = useState(0); // %
  const [targetDistance, setTargetDistance] = useState(5000); // Lightyears
  const [firing, setFiring] = useState(false);
  const [inhabited, setInhabited] = useState(false);

  useEffect(() => {
    // Simulate Mirror Alignment
    const align = setInterval(() => {
       if (!firing) {
          setCoherence(prev => {
             // Slowly build coherence
             if (prev < 99) return prev + 1.5;
             // Micro-fluctuations at peak
             return 99 + (Math.random() * 0.9);
          });
       }
    }, 100);

    return () => clearInterval(align);
  }, [firing]);

  const canFire = coherence > 95 && !inhabited && targetDistance <= 10000;

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-rose-500">Nicoll-Dyson</h2>
          <p className="text-xs text-slate-400">Stellar Phased-Array Laser</p>
        </div>
        <button 
           onMouseDown={() => canFire && setFiring(true)}
           onMouseUp={() => setFiring(false)}
           onMouseLeave={() => setFiring(false)}
           disabled={!canFire}
           className={`px-3 py-1 font-bold text-[10px] rounded border transition-all ${firing ? 'bg-white text-black border-white shadow-[0_0_30px_#fff]' : canFire ? 'bg-rose-900/50 text-rose-400 border-rose-800 hover:bg-rose-800' : 'bg-slate-800 text-slate-500 border-slate-700 cursor-not-allowed'}`}
        >
           {firing ? 'FIRING BEAM' : 'AUTHORIZE FIRE'}
        </button>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex items-center shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* The Star and Mirrors (Left side) */}
         <div className="absolute left-[-20px] top-1/2 -translate-y-1/2 w-24 h-24 rounded-full bg-yellow-500 shadow-[0_0_40px_#eab308]"></div>
         
         {/* Phased Array Mirrors focusing the light */}
         <div className="absolute left-[80px] top-0 bottom-0 w-8 flex flex-col justify-around">
            {[...Array(8)].map((_, i) => (
               <div key={i} className="w-2 h-4 bg-slate-300 rounded shadow-[0_0_5px_#fff]" style={{ transform: `rotate(${i > 3 ? 15 : -15}deg)` }}></div>
            ))}
         </div>

         {/* The Target (Right side) */}
         <div className="absolute right-[20px] top-1/2 -translate-y-1/2 w-8 h-8 rounded-full border border-rose-500/50 flex items-center justify-center">
            <div className={`w-2 h-2 rounded-full ${inhabited ? 'bg-emerald-500 shadow-[0_0_10px_#10b981]' : 'bg-slate-500'} ${firing ? 'animate-ping bg-rose-500 shadow-[0_0_20px_#f43f5e]' : ''}`}></div>
            {/* Crosshairs */}
            <div className="absolute w-full h-px bg-rose-500/30"></div>
            <div className="absolute h-full w-px bg-rose-500/30"></div>
         </div>

         {/* The Beam */}
         <div className="absolute left-[90px] right-[20px] top-1/2 -translate-y-1/2 h-10 flex items-center">
            {/* Ambient focusing light */}
            <div className="w-full h-full bg-gradient-to-r from-yellow-300/20 to-rose-500/0" style={{ opacity: coherence / 100 }}></div>
            
            {/* Main Laser Pulse */}
            <div className={`absolute left-0 w-full bg-white transition-all duration-75 ${firing ? 'h-6 shadow-[0_0_50px_#fff,0_0_100px_#f43f5e] opacity-100' : 'h-px opacity-0'}`}></div>
         </div>

      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Beam Coherence</div>
            <div className={`text-lg font-mono font-bold ${coherence > 95 ? 'text-emerald-400' : 'text-amber-400'}`}>
               {coherence.toFixed(2)} <span className="text-xs text-slate-500">%</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Target Distance</div>
            <div className={`text-lg font-mono font-bold ${targetDistance > 10000 ? 'text-red-400' : 'text-slate-300'}`}>
               {targetDistance} <span className="text-xs">LY</span>
            </div>
         </div>
      </div>

      <div className="flex justify-between items-center bg-slate-950 rounded border border-slate-800 p-2 text-[10px] font-mono">
         <button 
            onClick={() => setInhabited(!inhabited)}
            className={`px-2 py-1 rounded border ${inhabited ? 'bg-emerald-900/30 text-emerald-400 border-emerald-800' : 'bg-slate-800 text-slate-500 border-slate-700'}`}
         >
            {inhabited ? 'TARGET INHABITED' : 'TARGET BARREN'}
         </button>
         <span className={!canFire ? 'text-red-400' : 'text-emerald-400'}>
            {!canFire ? (inhabited ? 'VIOLATES DIRECTIVE 7' : 'COHERENCE TOO LOW') : 'SOLUTION LOCKED'}
         </span>
      </div>
    </div>
  );
};
