import React, { useState, useEffect } from 'react';

export const FlightEnvelope: React.FC = () => {
  const [mach, setMach] = useState(5.0);
  const [altitude, setAltitude] = useState(80000); // feet
  const [temp, setTemp] = useState(1200);

  useEffect(() => {
    // Simulate acceleration from Mach 5 to Mach 10
    const flight = setInterval(() => {
      setMach(prev => {
         const next = prev + 0.05;
         if (next >= 10.5) return 5.0; // Loop simulation
         return next;
      });
      
      setAltitude(prev => prev + (Math.random() - 0.2) * 50); // Climbing slightly
    }, 100);

    return () => clearInterval(flight);
  }, []);

  // Temperature scales roughly with Mach^2
  useEffect(() => {
     setTemp(200 + (mach * mach * 18));
  }, [mach]);

  const isCritical = temp > 2000;

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-orange-500">Hypersonic Scramjet</h2>
          <p className="text-xs text-slate-400">Flight Envelope Telemetry</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-mono border ${isCritical ? 'bg-red-900/50 text-red-400 border-red-800 animate-pulse' : 'bg-orange-900/30 text-orange-400 border-orange-800'}`}>
          {isCritical ? 'ABLATION CRITICAL' : 'NOMINAL'}
        </div>
      </div>

      <div className="bg-[#0f172a] p-4 rounded border border-slate-800 mb-4 h-[160px] relative overflow-hidden flex items-center">
         
         {/* Wind Tunnel Flow lines (moving left) */}
         <div className="absolute inset-0 opacity-20">
            {[...Array(10)].map((_, i) => (
               <div 
                  key={i} 
                  className="h-px bg-white absolute" 
                  style={{
                     top: `${i * 10}%`,
                     left: '0',
                     right: '0',
                     animation: `slide-left ${0.5 / (mach/5)}s linear infinite`
                  }}
               ></div>
            ))}
         </div>

         {/* The Scramjet Vehicle (Waverider shape) */}
         <div className="relative z-10 w-32 h-10 ml-8">
            <svg viewBox="0 0 100 40" className="w-full h-full drop-shadow-lg">
               {/* Body */}
               <path d="M0,20 L80,0 L100,20 L80,40 Z" fill="#334155" stroke="#94a3b8" strokeWidth="1"/>
               {/* Engine Inlet */}
               <path d="M40,20 L60,20 L70,30 L50,30 Z" fill="#0f172a" />
               {/* Exhaust Plume */}
               <path 
                  d="M0,20 L-40,10 L-40,30 Z" 
                  fill="url(#thrust)" 
                  className="animate-pulse"
                  style={{ opacity: mach > 6 ? 1 : 0.5 }}
               />
               <defs>
                  <linearGradient id="thrust" x1="1" y1="0" x2="0" y2="0">
                     <stop offset="0%" stopColor="#38bdf8" />
                     <stop offset="100%" stopColor="transparent" />
                  </linearGradient>
               </defs>
            </svg>

            {/* Oblique Shockwave Viz */}
            <div 
               className="absolute top-1/2 right-0 w-32 h-px bg-cyan-400/50 transform origin-right"
               style={{ transform: `rotate(${-15 - (10/mach)}deg)` }}
            ></div>
            <div 
               className="absolute top-1/2 right-0 w-32 h-px bg-cyan-400/50 transform origin-right"
               style={{ transform: `rotate(${15 + (10/mach)}deg)` }}
            ></div>

            {/* Nose Cone Heating Glow */}
            <div 
               className="absolute top-1/2 right-0 w-4 h-4 rounded-full filter blur-md transform -translate-y-1/2 translate-x-2"
               style={{ 
                  backgroundColor: isCritical ? '#ef4444' : '#f97316',
                  opacity: Math.min(1, (temp - 500) / 1500)
               }}
            ></div>
         </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Velocity</div>
            <div className="text-lg font-mono font-bold text-sky-400">Mach {mach.toFixed(2)}</div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800 relative overflow-hidden">
            <div className="text-[10px] uppercase text-slate-500 mb-1 z-10 relative">Leading Edge</div>
            <div className={`text-lg font-mono font-bold z-10 relative ${isCritical ? 'text-red-400' : 'text-orange-400'}`}>
               {temp.toFixed(0)} <span className="text-xs">°C</span>
            </div>
            <div 
               className={`absolute bottom-0 left-0 right-0 opacity-20 ${isCritical ? 'bg-red-500' : 'bg-orange-500'}`}
               style={{ height: `${(temp / 2500) * 100}%` }}
            ></div>
         </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Alt: <span className="text-white">{altitude.toFixed(0)} ft</span></span>
         <span>Combustion: <span className="text-emerald-400">Supersonic</span></span>
      </div>

      <style>{`
        @keyframes slide-left {
          from { transform: translateX(100%); }
          to { transform: translateX(-100%); }
        }
      `}</style>
    </div>
  );
};
