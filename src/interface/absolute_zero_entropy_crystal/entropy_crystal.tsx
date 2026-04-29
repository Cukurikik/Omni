import React, { useState, useEffect } from 'react';

export const EntropyCrystal: React.FC = () => {
  const [temperatureNk, setTemperatureNk] = useState(10); // nanoKelvins
  const [cooling, setCooling] = useState(true);
  const [dataIntact, setDataIntact] = useState(true);

  useEffect(() => {
    const cryo = setInterval(() => {
       if (cooling) {
          setTemperatureNk(prev => {
             const next = prev - 0.5;
             if (next <= 0) return 0; // Absolute zero achieved
             return next;
          });
       } else {
          setTemperatureNk(prev => {
             const next = prev + 1.5;
             if (next > 1.0) setDataIntact(false); // Over 1nK causes data corruption
             return next;
          });
       }
    }, 200);

    return () => clearInterval(cryo);
  }, [cooling]);

  // Reset if we re-cool after a failure
  useEffect(() => {
     if (temperatureNk <= 0 && !dataIntact) {
        // Can't bring corrupted data back, but we can reset for UI purposes
        setDataIntact(true);
     }
  }, [temperatureNk, dataIntact]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-cyan-300">Entropy Crystal</h2>
          <p className="text-xs text-slate-400">Absolute Zero Storage</p>
        </div>
        <button 
           onClick={() => setCooling(!cooling)}
           className={`px-3 py-1 font-bold text-[10px] rounded border transition-colors ${cooling ? 'bg-cyan-900/50 text-cyan-300 border-cyan-600 shadow-[0_0_15px_#06b6d4]' : 'bg-slate-800 text-slate-500 border-slate-700 hover:bg-slate-700'}`}
        >
           {cooling ? 'LASER COOLING ACTIVE' : 'COOLING OFFLINE'}
        </button>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex items-center justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)] perspective-[600px]">
         
         {/* Environmental heat (Red background glow that fades as it cools) */}
         <div className="absolute inset-0 transition-opacity duration-500" style={{ opacity: temperatureNk / 10, background: 'radial-gradient(circle at center, rgba(239,68,68,0.2) 0%, transparent 70%)' }}></div>

         {/* The Crystal Lattice */}
         <div 
            className={`relative w-32 h-32 transform-style-3d transition-transform duration-1000 ${temperatureNk <= 0 ? 'animate-[spin_20s_linear_infinite]' : ''}`}
            style={{ 
               transform: `rotateX(60deg) rotateZ(45deg) ${temperatureNk > 1 ? `translate(${Math.random()*4-2}px, ${Math.random()*4-2}px)` : ''}` // Shake if hot
            }}
         >
            {/* Base grid */}
            <div className={`absolute inset-0 border border-cyan-500/50 ${temperatureNk <= 0 ? 'shadow-[0_0_20px_#06b6d4]' : ''} ${!dataIntact ? 'border-red-500 shadow-[0_0_20px_#ef4444]' : ''}`}>
               {/* Internal atoms (BEC state) */}
               <div className="absolute inset-0 bg-[linear-gradient(rgba(6,182,212,0.3)_1px,transparent_1px),linear-gradient(90deg,rgba(6,182,212,0.3)_1px,transparent_1px)] bg-[size:20%_20%]"></div>
               
               {/* Condensate Glow (only at absolute zero) */}
               {temperatureNk <= 0 && (
                  <div className="absolute inset-0 bg-cyan-400/20 mix-blend-screen animate-pulse"></div>
               )}
            </div>
            
            {/* Top grid (3D depth) */}
            <div 
               className={`absolute inset-0 border border-cyan-400/50 ${temperatureNk <= 0 ? 'shadow-[0_0_10px_#22d3ee]' : ''} ${!dataIntact ? 'border-red-500' : ''}`}
               style={{ transform: 'translateZ(32px)' }}
            >
               <div className="absolute inset-0 bg-[linear-gradient(rgba(34,211,238,0.3)_1px,transparent_1px),linear-gradient(90deg,rgba(34,211,238,0.3)_1px,transparent_1px)] bg-[size:20%_20%]"></div>
            </div>

            {/* Connecting edges */}
            <div className={`absolute top-0 left-0 w-[32px] h-px ${!dataIntact ? 'bg-red-500' : 'bg-cyan-500/50'}`} style={{ transformOrigin: 'left', transform: 'rotateY(90deg)' }}></div>
            <div className={`absolute top-0 right-0 w-[32px] h-px ${!dataIntact ? 'bg-red-500' : 'bg-cyan-500/50'}`} style={{ transformOrigin: 'right', transform: 'rotateY(-90deg)' }}></div>
            <div className={`absolute bottom-0 left-0 w-[32px] h-px ${!dataIntact ? 'bg-red-500' : 'bg-cyan-500/50'}`} style={{ transformOrigin: 'left', transform: 'rotateY(90deg)' }}></div>
            <div className={`absolute bottom-0 right-0 w-[32px] h-px ${!dataIntact ? 'bg-red-500' : 'bg-cyan-500/50'}`} style={{ transformOrigin: 'right', transform: 'rotateY(-90deg)' }}></div>
         </div>

         {/* Phonon Cancellation Lasers */}
         {cooling && temperatureNk > 0 && (
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none mix-blend-screen opacity-50">
               <div className="w-full h-px bg-cyan-300 transform rotate-45"></div>
               <div className="w-full h-px bg-cyan-300 transform -rotate-45"></div>
            </div>
         )}
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Temperature</div>
            <div className={`text-lg font-mono font-bold ${temperatureNk <= 0 ? 'text-cyan-300' : (temperatureNk > 1 ? 'text-red-400' : 'text-slate-300')}`}>
               {temperatureNk.toFixed(1)} <span className="text-xs text-slate-500">nK</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">State</div>
            <div className={`text-lg font-mono font-bold ${temperatureNk <= 0 ? 'text-cyan-400' : 'text-slate-500'} truncate`}>
               {temperatureNk <= 0 ? 'B.E.C.' : 'LATTICE'}
            </div>
         </div>
      </div>

      <div className="w-full bg-slate-950 rounded border border-slate-800 p-2 text-[10px] font-mono text-center">
         <span className={!dataIntact ? 'text-red-400 font-bold' : (temperatureNk <= 0 ? 'text-cyan-300 font-bold' : 'text-slate-400')}>
            {!dataIntact 
               ? 'CORRUPTION: THERMAL JITTER EXCEEDED 1 nK' 
               : (temperatureNk <= 0 
                  ? 'ABSOLUTE ZERO REACHED - ENTROPY IS ZERO' 
                  : 'CANCELLING LATTICE PHONONS...')}
         </span>
      </div>
    </div>
  );
};
