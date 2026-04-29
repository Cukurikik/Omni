import React, { useState, useEffect } from 'react';

export const FaultStressMap: React.FC = () => {
  const [pWaveRadius, setPWaveRadius] = useState(0);
  const [sWaveRadius, setSWaveRadius] = useState(0);
  const [quakeActive, setQuakeActive] = useState(false);

  useEffect(() => {
    // Simulate an earthquake event every 8 seconds
    const event = setInterval(() => {
       setQuakeActive(true);
       setPWaveRadius(0);
       setSWaveRadius(0);

       // Expand waves (P waves are roughly 1.7x faster than S waves)
       const wave = setInterval(() => {
          setPWaveRadius(prev => {
             if (prev > 100) {
                clearInterval(wave);
                setTimeout(() => setQuakeActive(false), 2000);
                return prev;
             }
             return prev + 4; // Fast P-Wave
          });
          setSWaveRadius(prev => prev + 2.3); // Slower S-Wave
       }, 50);

    }, 8000);

    return () => clearInterval(event);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-red-500">Seismic Network</h2>
          <p className="text-xs text-slate-400">Earthquake Early Warning</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-mono border ${quakeActive ? 'bg-red-900/50 text-red-400 border-red-800 animate-pulse' : 'bg-slate-800 text-slate-400 border-slate-700'}`}>
          {quakeActive ? 'M8.2 DETECTED' : 'MONITORING'}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[180px] relative overflow-hidden flex items-center justify-center">
         
         {/* Map Background (Mock Fault Line) */}
         <svg className="absolute inset-0 w-full h-full opacity-30">
            <path d="M20,0 Q 30,50 40,100" fill="none" stroke="#ef4444" strokeWidth="2" strokeDasharray="4 2"/>
            {/* Coastal City */}
            <circle cx="70" cy="50" r="3" fill="#94a3b8" />
            <text x="75" y="53" fill="#94a3b8" fontSize="8" fontFamily="monospace">TOKYO</text>
         </svg>

         {quakeActive && (
            <>
               {/* Epicenter */}
               <div className="absolute w-2 h-2 bg-white rounded-full shadow-[0_0_10px_#fff] z-10" style={{ left: '35%', top: '60%' }}></div>
               
               {/* P-Wave (Fast, Harmless, Blue) */}
               <div 
                  className="absolute rounded-full border border-sky-500/50"
                  style={{ 
                     left: `calc(35% + 4px - ${pWaveRadius}px)`, 
                     top: `calc(60% + 4px - ${pWaveRadius}px)`,
                     width: `${pWaveRadius * 2}px`, 
                     height: `${pWaveRadius * 2}px`
                  }}
               ></div>

               {/* S-Wave (Slow, Destructive, Red) */}
               <div 
                  className="absolute rounded-full border border-red-500/80 bg-red-500/10"
                  style={{ 
                     left: `calc(35% + 4px - ${sWaveRadius}px)`, 
                     top: `calc(60% + 4px - ${sWaveRadius}px)`,
                     width: `${sWaveRadius * 2}px`, 
                     height: `${sWaveRadius * 2}px`
                  }}
               ></div>
            </>
         )}

      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4 text-center">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Time to Impact</div>
            <div className={`text-lg font-mono font-bold ${quakeActive ? 'text-orange-400' : 'text-slate-500'}`}>
               {quakeActive ? Math.max(0, 15 - Math.floor(sWaveRadius/5)) : '--'} <span className="text-xs">sec</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Tsunami Threat</div>
            <div className={`text-lg font-mono font-bold ${quakeActive ? 'text-red-400 animate-pulse' : 'text-slate-500'}`}>
               {quakeActive ? 'CRITICAL' : 'NONE'}
            </div>
         </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Subsea Array: <span className="text-emerald-400">Online</span></span>
         <span>Trains/Elevators: <span className={quakeActive ? 'text-red-400' : 'text-emerald-400'}>{quakeActive ? 'HALTED' : 'Normal'}</span></span>
      </div>
    </div>
  );
};
