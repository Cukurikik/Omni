import React, { useState, useEffect } from 'react';

export const MagneticField: React.FC = () => {
  const [beta, setBeta] = useState(0.02);
  const troyonLimit = 0.035;

  useEffect(() => {
    // Simulate plasma heating and pressure build-up
    const heating = setInterval(() => {
      setBeta(prev => {
         const noise = (Math.random() - 0.45) * 0.002;
         const next = prev + 0.0005 + noise;
         // If it quenches (exceeds limit), reset
         if (next > troyonLimit + 0.002) return 0.01;
         return Math.max(0.01, next);
      });
    }, 200);

    return () => clearInterval(heating);
  }, []);

  const isQuenching = beta > troyonLimit;

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-violet-400">Tokamak Reactor</h2>
          <p className="text-xs text-slate-400">MHD Plasma Containment</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-mono border ${isQuenching ? 'bg-red-900/50 text-red-400 border-red-800 animate-pulse' : 'bg-violet-900/30 text-violet-400 border-violet-800'}`}>
          {isQuenching ? 'THERMAL QUENCH' : 'CONTAINED'}
        </div>
      </div>

      <div className="bg-black p-4 rounded border border-slate-800 mb-4 h-[200px] flex items-center justify-center relative overflow-hidden">
         {/* Tokamak Cross-Section View */}
         <div className="w-40 h-40 border-4 border-slate-700 rounded-full flex items-center justify-center relative shadow-[0_0_20px_rgba(0,0,0,0.5)_inset]">
            
            {/* The Plasma (D-Shaped roughly) */}
            <div 
               className={`absolute rounded-full filter blur-md transition-all duration-75 ${isQuenching ? 'bg-red-500 animate-ping' : 'bg-violet-500'}`}
               style={{ 
                  width: `${(beta / troyonLimit) * 120}px`,
                  height: `${(beta / troyonLimit) * 140}px`,
                  opacity: Math.min(1, 0.5 + (beta / troyonLimit)),
                  boxShadow: `0 0 ${isQuenching ? '50px #ef4444' : '30px #8b5cf6'}`
               }}
            ></div>
            
            {/* Superconducting Coils (Dots around) */}
            {[...Array(12)].map((_, i) => (
               <div 
                  key={i} 
                  className="absolute w-2 h-2 bg-sky-400 rounded-full"
                  style={{
                     transform: `rotate(${i * 30}deg) translateY(-85px)`
                  }}
               ></div>
            ))}
         </div>
      </div>
      
      <div className="space-y-2 mb-4">
         <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400">Plasma Beta (β)</span>
            <span className={`font-bold font-mono ${isQuenching ? 'text-red-400' : 'text-violet-400'}`}>{beta.toFixed(4)}</span>
         </div>
         {/* Stability Gauge */}
         <div className="w-full h-1 bg-slate-800 rounded relative">
            <div className={`absolute top-0 bottom-0 left-0 transition-all ${isQuenching ? 'bg-red-500' : 'bg-violet-500'}`} style={{ width: `${Math.min(100, (beta / 0.04) * 100)}%` }}></div>
            <div className="absolute top-0 bottom-0 w-px bg-white z-10" style={{ left: `${(troyonLimit / 0.04) * 100}%` }}></div>
         </div>
         <div className="text-[8px] text-right text-slate-500 font-mono">Troyon Limit: {troyonLimit}</div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Temp: <span className="text-white">152M K</span></span>
         <span>Field: <span className="text-sky-400">11.8 Tesla</span></span>
      </div>
    </div>
  );
};
