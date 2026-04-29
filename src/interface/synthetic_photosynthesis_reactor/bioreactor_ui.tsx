import React, { useState, useEffect } from 'react';

export const BioreactorUi: React.FC = () => {
  const [co2Ppm, setCo2Ppm] = useState(420);
  const [efficiency, setEfficiency] = useState(25); // %
  const [active, setActive] = useState(true);

  useEffect(() => {
    // Simulate Global Carbon Drawdown
    const reactor = setInterval(() => {
       if (active) {
          // Rapidly drawing down CO2
          setCo2Ppm(prev => {
             const next = prev - 0.5;
             if (next < 180) {
                setActive(false); // Auto-shutdown to prevent plant starvation
             }
             return next;
          });
       } else {
          // Natural emissions pushing it slowly back up
          setCo2Ppm(prev => Math.min(450, prev + 0.1));
       }
       
       // Efficiency fluctuates based on simulated cloud cover (sunlight)
       setEfficiency(25 + (Math.random() - 0.5) * 5);
       
    }, 100);

    return () => clearInterval(reactor);
  }, [active]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-emerald-500">Bioreactor</h2>
          <p className="text-xs text-slate-400">Artificial Leaf Array</p>
        </div>
        <button 
           onClick={() => setActive(!active)}
           className={`px-3 py-1 font-bold text-[10px] rounded border transition-colors ${active ? 'bg-emerald-900/50 text-emerald-400 border-emerald-800' : 'bg-red-900/50 text-red-400 border-red-800'}`}
        >
           {active ? 'ACTIVE DRAWDOWN' : 'SYSTEM HALTED'}
        </button>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex flex-col items-center justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* Sunlight (Photons) */}
         <div className={`absolute top-0 inset-x-0 h-24 bg-gradient-to-b from-yellow-300/20 to-transparent transition-opacity duration-1000 ${active ? 'opacity-100' : 'opacity-10'}`}></div>

         {/* The Photoelectrochemical Cell */}
         <div className="relative z-10 w-32 h-32 border-4 border-slate-700 rounded-b-3xl bg-slate-800/80 overflow-hidden shadow-[0_10px_20px_rgba(0,0,0,0.5)]">
            
            {/* Catalyst Surface */}
            <div className={`absolute bottom-0 w-full bg-emerald-500/30 border-t border-emerald-400 transition-all duration-1000 ${active ? 'h-24' : 'h-8'}`}>
               
               {/* Oxygen/Hydrogen Bubbles */}
               {active && [...Array(15)].map((_, i) => (
                  <div 
                     key={i} 
                     className="absolute w-1.5 h-1.5 bg-white/60 rounded-full"
                     style={{
                        left: `${Math.random() * 100}%`,
                        bottom: '0',
                        animation: `bubble ${1 + Math.random() * 2}s linear infinite`,
                        animationDelay: `${Math.random() * 2}s`
                     }}
                  ></div>
               ))}
            </div>

            {/* CO2 Intake */}
            {active && (
               <div className="absolute top-2 left-1/2 -translate-x-1/2 text-[8px] font-mono text-slate-400 animate-pulse flex flex-col items-center">
                  <span>↓ CO₂</span>
                  <span>↓ H₂O</span>
               </div>
            )}
         </div>

         {/* Fuel Output Pipeline */}
         <div className="w-4 h-8 bg-slate-700 border-x-2 border-slate-600 rounded-b relative overflow-hidden">
            <div className={`absolute bottom-0 w-full bg-sky-500 transition-all duration-300 ${active ? 'h-full' : 'h-0'}`}></div>
         </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Atmospheric CO2</div>
            <div className={`text-lg font-mono font-bold ${co2Ppm < 180 ? 'text-red-400 animate-pulse' : 'text-emerald-400'}`}>
               {co2Ppm.toFixed(1)} <span className="text-xs">ppm</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Quantum Yield</div>
            <div className={`text-lg font-mono font-bold ${active ? 'text-sky-400' : 'text-slate-500'}`}>
               {active ? efficiency.toFixed(1) : '0.0'} <span className="text-xs">%</span>
            </div>
         </div>
      </div>

      <div className="grid grid-cols-1 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded text-center">
         <span className={co2Ppm < 180 ? 'text-red-400' : 'text-white'}>
            {co2Ppm < 180 ? 'FLORA STARVATION RISK - HALT REACTOR' : 'SYNTHESIS NOMINAL'}
         </span>
      </div>

      <style>{`
        @keyframes bubble {
          0% { transform: translateY(0) scale(1); opacity: 1; }
          100% { transform: translateY(-80px) scale(1.5); opacity: 0; }
        }
      `}</style>
    </div>
  );
};
