import React, { useState, useEffect } from 'react';

export const GlobalWeather: React.FC = () => {
  const [rotation, setRotation] = useState(0);

  useEffect(() => {
    const storm = setInterval(() => {
      // Rotate the hurricane eye
      setRotation(prev => (prev - 10) % 360);
    }, 50);

    return () => clearInterval(storm);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-blue-400">Exascale Weather</h2>
          <p className="text-xs text-slate-400">Global Navier-Stokes CFD</p>
        </div>
        <div className="px-2 py-1 rounded text-[10px] font-bold font-mono bg-red-900/50 text-red-400 border border-red-800 animate-pulse">
          CAT 5 DETECTED
        </div>
      </div>

      <div className="bg-[#0f172a] p-4 rounded border border-slate-800 mb-4 h-[200px] flex items-center justify-center relative overflow-hidden">
         
         {/* Map Background */}
         <div className="absolute inset-0 opacity-30">
            {/* Mock Florida/Gulf Coast SVG */}
            <svg viewBox="0 0 100 100" className="w-full h-full fill-emerald-800">
               <path d="M0,0 L100,0 L100,20 L60,40 L70,80 L60,90 L40,60 L20,30 Z" />
            </svg>
         </div>

         {/* The Hurricane */}
         <div 
            className="absolute right-10 bottom-10 w-32 h-32 flex items-center justify-center"
            style={{ transform: `rotate(${rotation}deg)` }}
         >
            {/* Spiral Bands */}
            <div className="absolute inset-0 bg-[conic-gradient(from_0deg,transparent,rgba(255,255,255,0.4),rgba(56,189,248,0.8),transparent)] rounded-full blur-sm"></div>
            <div className="absolute inset-2 bg-[conic-gradient(from_180deg,transparent,rgba(255,255,255,0.4),rgba(56,189,248,0.8),transparent)] rounded-full blur-sm"></div>
            
            {/* The Eye */}
            <div className="absolute w-4 h-4 bg-slate-900 border-2 border-white rounded-full shadow-[0_0_15px_#fff]"></div>
         </div>
         
         {/* Predicted Track Cone */}
         <svg className="absolute inset-0 w-full h-full z-10 opacity-40">
            <path d="M70,70 Q 50,50 30,30 L 10,50 Q 40,70 70,70" fill="rgba(239, 68, 68, 0.3)" stroke="#ef4444" strokeWidth="1" strokeDasharray="4 2"/>
         </svg>

      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Max Sustained</div>
            <div className="text-lg font-mono font-bold text-red-400">165 <span className="text-xs">MPH</span></div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Storm Surge</div>
            <div className="text-lg font-mono font-bold text-orange-400">18.5 <span className="text-xs">FT</span></div>
         </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Resolution: <span className="text-white">1.2 km Global</span></span>
         <span>Compute: <span className="text-emerald-400">MPI 100k Cores</span></span>
      </div>
    </div>
  );
};
