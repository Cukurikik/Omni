import React, { useState, useEffect } from 'react';

export const QuarkGluonPlasma: React.FC = () => {
  const [fieldTesla, setFieldTesla] = useState(50.0);
  const [stability, setStability] = useState(100);
  const [breachAlert, setBreachAlert] = useState(false);

  useEffect(() => {
    // Simulate magnetic field fluctuations and strangelet stability
    const containment = setInterval(() => {
       setFieldTesla(prev => {
          const next = prev + (Math.random() - 0.5) * 0.5;
          
          if (next < 45.0) {
             setBreachAlert(true);
             setStability(prevStab => Math.max(0, prevStab - 10));
          } else {
             setBreachAlert(false);
             setStability(100);
          }
          return next;
       });
    }, 200);

    return () => clearInterval(containment);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-rose-500">Strangelet Trap</h2>
          <p className="text-xs text-slate-400">Quark-Gluon Plasma</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-mono border ${breachAlert ? 'bg-red-900/80 text-white border-red-500 shadow-[0_0_15px_#ef4444] animate-[pulse_0.2s_ease-in-out_infinite]' : 'bg-slate-800 text-slate-400 border-slate-700'}`}>
          {breachAlert ? 'ICE-9 BREACH IMMINENT' : 'CONTAINED'}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex flex-col items-center justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* Magnetic Confinement Field Lines */}
         <div className="absolute inset-0 flex items-center justify-center opacity-50">
            <div className={`w-32 h-32 rounded-full border-2 transition-colors duration-300 ${breachAlert ? 'border-red-500/30 animate-pulse' : 'border-sky-500/30'}`}></div>
            <div className={`absolute w-24 h-48 rounded-full border border-sky-400/20 rotate-45`}></div>
            <div className={`absolute w-24 h-48 rounded-full border border-sky-400/20 -rotate-45`}></div>
         </div>

         {/* The Strangelet (Quark-Gluon Plasma) */}
         <div className="relative z-10 flex items-center justify-center animate-[spin_3s_linear_infinite]">
            {/* Color-Flavor Locked core */}
            <div className={`w-12 h-12 rounded-full blur-md absolute transition-colors duration-300 ${breachAlert ? 'bg-red-600' : 'bg-rose-500'}`}></div>
            <div className="w-6 h-6 rounded-full bg-white shadow-[0_0_20px_#fff] flex items-center justify-center overflow-hidden">
               {/* Swirling Quarks (Red, Green, Blue) */}
               <div className="w-full h-full relative animate-[spin_0.5s_linear_infinite_reverse]">
                  <div className="absolute top-0 left-1 w-2 h-2 bg-red-500 rounded-full mix-blend-screen"></div>
                  <div className="absolute bottom-1 right-0 w-2 h-2 bg-green-500 rounded-full mix-blend-screen"></div>
                  <div className="absolute bottom-1 left-0 w-2 h-2 bg-blue-500 rounded-full mix-blend-screen"></div>
               </div>
            </div>
         </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Magnetic Field</div>
            <div className={`text-lg font-mono font-bold ${fieldTesla < 45 ? 'text-red-400' : 'text-sky-400'}`}>
               {fieldTesla.toFixed(2)} <span className="text-xs">T</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800 relative overflow-hidden">
            <div className="text-[10px] uppercase text-slate-500 mb-1 relative z-10">CFL Stability</div>
            <div className={`text-lg font-mono font-bold relative z-10 ${stability < 100 ? 'text-red-400' : 'text-white'}`}>
               {stability}%
            </div>
            <div className={`absolute bottom-0 left-0 right-0 ${stability < 100 ? 'bg-red-500/30' : 'bg-rose-500/20'}`} style={{ height: `${stability}%` }}></div>
         </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Charge: <span className="text-white">-2.5e-18 C</span></span>
         <span>Quarks: <span className="text-emerald-400">Up, Down, Strange</span></span>
      </div>
    </div>
  );
};
