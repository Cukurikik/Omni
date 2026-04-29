import React, { useState, useEffect } from 'react';

export const PulsarNavUi: React.FC = () => {
  const [lockedPulsars, setLockedPulsars] = useState(0);
  const [uncertainty, setUncertainty] = useState(150000); // km
  const [status, setStatus] = useState<'ACQUIRING' | 'LOCKING' | 'LOCKED'>('ACQUIRING');
  
  // Pulsar spin rates (Hz)
  const pulsars = [
     { name: "PSR B1937+21", freq: 641.92 },
     { name: "PSR J1748-2446ad", freq: 716.36 },
     { name: "PSR B1919+21", freq: 0.74 },
     { name: "PSR J0437-4715", freq: 173.68 }
  ];

  useEffect(() => {
    // Simulate acquisition sequence
    const nav = setInterval(() => {
       setLockedPulsars(prev => {
          if (prev < 4) return prev + 1;
          return 4;
       });
       
       setUncertainty(prev => {
          if (prev > 10) return prev * 0.4;
          return 3.14; // Reached high precision
       });
    }, 1500);

    return () => clearInterval(nav);
  }, []);

  useEffect(() => {
     if (lockedPulsars < 4) setStatus('ACQUIRING');
     else if (uncertainty > 50) setStatus('LOCKING');
     else setStatus('LOCKED');
  }, [lockedPulsars, uncertainty]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-cyan-400">Galactic GPS</h2>
          <p className="text-xs text-slate-400">Pulsar Timing Array</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-mono border ${status === 'LOCKED' ? 'bg-emerald-900/50 text-emerald-400 border-emerald-800 shadow-[0_0_10px_#10b981]' : 'bg-amber-900/50 text-amber-400 border-amber-800 animate-pulse'}`}>
          {status}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex items-center justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* Galactic Coordinate Grid */}
         <div className="absolute inset-0 border border-cyan-900/30 rounded-full scale-150 flex items-center justify-center">
            <div className="w-3/4 h-3/4 border border-cyan-800/30 rounded-full"></div>
            <div className="w-1/2 h-1/2 border border-cyan-700/30 rounded-full absolute"></div>
            <div className="w-1/4 h-1/4 border border-cyan-600/40 rounded-full absolute"></div>
         </div>

         {/* Ship Position (Center) */}
         <div className="relative z-10 w-2 h-2 bg-white rounded-full shadow-[0_0_10px_#fff]">
            {/* Uncertainty Error Ellipse */}
            {status !== 'LOCKED' && (
               <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full border border-amber-500/50 bg-amber-500/10 transition-all duration-1000 animate-pulse" style={{ width: Math.max(10, uncertainty / 1000) + 'px', height: Math.max(10, uncertainty / 1000) + 'px' }}></div>
            )}
         </div>

         {/* Pulsar Beacons */}
         {pulsars.map((p, i) => {
            const isLocked = i < lockedPulsars;
            const angle = (i * 90) + 45;
            const radius = 60 + Math.random() * 20;
            const x = 50 + Math.cos(angle * Math.PI / 180) * radius;
            const y = 50 + Math.sin(angle * Math.PI / 180) * radius;
            
            return (
               <React.Fragment key={i}>
                  {/* Pulsar Body */}
                  <div 
                     className={`absolute w-3 h-3 rounded-full flex items-center justify-center ${isLocked ? 'bg-cyan-500 shadow-[0_0_15px_#06b6d4]' : 'bg-slate-600'}`}
                     style={{ left: `${x}%`, top: `${y}%`, transform: 'translate(-50%, -50%)' }}
                  >
                     {/* Fast Spin Animation (approximating Hz) */}
                     {isLocked && (
                        <div className="w-full h-full border-2 border-white rounded-full border-t-transparent animate-spin" style={{ animationDuration: `${1/p.freq}s` }}></div>
                     )}
                  </div>
                  
                  {/* Triangulation Beam */}
                  {isLocked && (
                     <svg className="absolute inset-0 w-full h-full pointer-events-none">
                        <line x1={`${x}%`} y1={`${y}%`} x2="50%" y2="50%" stroke={status === 'LOCKED' ? '#10b981' : '#06b6d4'} strokeWidth="1" strokeDasharray="2 4" opacity="0.6" className="animate-[dash_10s_linear_infinite]" />
                     </svg>
                  )}
               </React.Fragment>
            )
         })}
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Telemetry Links</div>
            <div className={`text-lg font-mono font-bold ${lockedPulsars < 4 ? 'text-amber-400' : 'text-emerald-400'}`}>
               {lockedPulsars} <span className="text-xs text-slate-500">/ 4</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Positional Error</div>
            <div className={`text-lg font-mono font-bold ${status === 'LOCKED' ? 'text-emerald-400' : 'text-amber-400'}`}>
               {uncertainty < 1000 ? uncertainty.toFixed(1) : (uncertainty / 1000).toFixed(0)} <span className="text-xs">{uncertainty < 1000 ? 'm' : 'km'}</span>
            </div>
         </div>
      </div>

      <div className="grid grid-cols-1 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded text-center">
         <span>Detector: <span className="text-white">Silicon Drift X-Ray Array</span></span>
      </div>
    </div>
  );
};
