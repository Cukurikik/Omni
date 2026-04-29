import React, { useState, useEffect } from 'react';

export const CmeDashboard: React.FC = () => {
  const [xrayFlux, setXrayFlux] = useState(1e-6); // C-class baseline
  const [cmeVelocity, setCmeVelocity] = useState(0);
  const [alertLevel, setAlertLevel] = useState<'NOMINAL' | 'M-CLASS' | 'X-CLASS (CARRINGTON)'>('NOMINAL');

  useEffect(() => {
    // Simulate Solar Weather cycle
    const sun = setInterval(() => {
       const isFlare = Math.random() > 0.8;
       
       if (isFlare) {
          // Jump to M or X class
          const newFlux = Math.random() > 0.7 ? 2.5e-4 : 5.0e-5; 
          setXrayFlux(newFlux);
          
          if (newFlux > 1e-4) {
             setAlertLevel('X-CLASS (CARRINGTON)');
             setCmeVelocity(2200); // Massive CME
          } else {
             setAlertLevel('M-CLASS');
             setCmeVelocity(800);
          }
       } else {
          // Exponential decay back to baseline
          setXrayFlux(prev => Math.max(1e-7, prev * 0.5));
          setCmeVelocity(prev => Math.max(0, prev - 100));
          if (xrayFlux < 1e-5) setAlertLevel('NOMINAL');
       }
    }, 2000);

    return () => clearInterval(sun);
  }, [xrayFlux]);

  // GOES Classification logic
  const getGoesClass = (flux: number) => {
     if (flux >= 1e-4) return `X${(flux / 1e-4).toFixed(1)}`;
     if (flux >= 1e-5) return `M${(flux / 1e-5).toFixed(1)}`;
     if (flux >= 1e-6) return `C${(flux / 1e-6).toFixed(1)}`;
     return `B${(flux / 1e-7).toFixed(1)}`;
  };

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-amber-500">Heliophysics</h2>
          <p className="text-xs text-slate-400">CME & Flare Predictor</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-bold border ${alertLevel === 'X-CLASS (CARRINGTON)' ? 'bg-red-900/80 text-white border-red-500 shadow-[0_0_15px_#ef4444] animate-[pulse_0.2s_ease-in-out_infinite]' : alertLevel === 'M-CLASS' ? 'bg-orange-900/50 text-orange-400 border-orange-600' : 'bg-slate-800 text-slate-400 border-slate-700'}`}>
          {alertLevel}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex items-center justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* Deep Space Background */}
         <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_left,_var(--tw-gradient-stops))] from-amber-900/20 via-transparent to-transparent"></div>

         {/* The Sun (Partial edge visible on left) */}
         <div 
            className="absolute left-[-150px] top-1/2 -translate-y-1/2 w-[300px] h-[300px] rounded-full bg-amber-500 blur-[2px] shadow-[0_0_80px_#f59e0b]"
            style={{ 
               background: 'radial-gradient(circle at 75% 50%, #fef08a 0%, #f59e0b 60%, #b45309 100%)' 
            }}
         >
            {/* Sunspots (Active Regions) */}
            <div className="absolute w-4 h-4 bg-amber-900 rounded-full blur-[1px]" style={{ right: '40px', top: '120px' }}></div>
            <div className="absolute w-6 h-6 bg-amber-900 rounded-full blur-[1px]" style={{ right: '60px', top: '160px' }}></div>
         </div>

         {/* Solar Flare Flash */}
         {alertLevel !== 'NOMINAL' && (
            <div className={`absolute left-[130px] top-[140px] w-20 h-20 rounded-full mix-blend-screen animate-ping ${alertLevel === 'X-CLASS (CARRINGTON)' ? 'bg-white shadow-[0_0_100px_#fff]' : 'bg-yellow-400/50 shadow-[0_0_50px_#facc15]'}`}></div>
         )}

         {/* Coronal Mass Ejection (CME) Plasma Cloud */}
         {cmeVelocity > 0 && (
            <div 
               className={`absolute h-32 rounded-full blur-xl animate-[cme-launch_2s_linear_forwards] ${alertLevel === 'X-CLASS (CARRINGTON)' ? 'bg-gradient-to-r from-yellow-300 to-red-500/0 w-64 opacity-80' : 'bg-gradient-to-r from-amber-500/50 to-orange-500/0 w-40 opacity-40'}`}
               style={{ top: '35%', left: '100px' }}
            ></div>
         )}

         {/* Earth (Target) */}
         <div className="absolute right-6 w-3 h-3 bg-blue-500 rounded-full shadow-[0_0_10px_#3b82f6]">
            {/* Magnetic Field (Deflecting solar wind) */}
            <div className={`absolute -inset-4 border-l-2 border-blue-400/50 rounded-full ${alertLevel === 'X-CLASS (CARRINGTON)' && 'border-red-500/80 animate-pulse'}`}></div>
         </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">X-Ray Flux (GOES)</div>
            <div className={`text-lg font-mono font-bold ${alertLevel === 'X-CLASS (CARRINGTON)' ? 'text-white' : 'text-amber-400'}`}>
               {getGoesClass(xrayFlux)} <span className="text-xs text-slate-500">({xrayFlux.toExponential(1)} W/m²)</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Plasma Velocity</div>
            <div className={`text-lg font-mono font-bold ${cmeVelocity > 2000 ? 'text-red-400' : 'text-sky-400'}`}>
               {cmeVelocity.toFixed(0)} <span className="text-xs">km/s</span>
            </div>
         </div>
      </div>

      <div className="w-full bg-slate-950 rounded border border-slate-800 p-2 text-xs font-mono text-center">
         <span className={alertLevel === 'X-CLASS (CARRINGTON)' ? 'text-red-400 animate-pulse' : 'text-emerald-400'}>
            {alertLevel === 'X-CLASS (CARRINGTON)' ? 'WARNING: SEVERE GRID IMPACT IN 20 HOURS' : 'POWER GRID SECURE'}
         </span>
      </div>

      <style>{`
        @keyframes cme-launch {
          0% { transform: translateX(0) scale(0.5); }
          100% { transform: translateX(250px) scale(2); opacity: 0; }
        }
      `}</style>
    </div>
  );
};
