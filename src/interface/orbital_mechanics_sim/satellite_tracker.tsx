import React, { useState, useEffect } from 'react';

export const SatelliteTracker: React.FC = () => {
  const [satAngle, setSatAngle] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      // Orbiting at ~7.6 km/s in Low Earth Orbit (simulated)
      setSatAngle(prev => (prev + 0.02) % (Math.PI * 2));
    }, 50);
    return () => clearInterval(interval);
  }, []);

  const earthRadius = 50;
  const orbitRadius = 80; // LEO
  
  const satX = 150 + orbitRadius * Math.cos(satAngle);
  const satY = 100 + orbitRadius * Math.sin(satAngle) * 0.4; // Inclined orbit simulation

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-sky-400">Orbital Mechanics</h2>
          <p className="text-xs text-slate-400">LEO Vis-Viva Simulation</p>
        </div>
        <div className="text-[10px] font-mono bg-sky-900/30 text-sky-400 border border-sky-800 px-2 py-1 rounded">
          OMNI-SAT-1
        </div>
      </div>

      <div className="bg-[#050510] p-0 rounded border border-slate-800 relative h-[200px] mb-4 flex items-center justify-center overflow-hidden">
         
         {/* Deep Space Background */}
         <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-slate-900 via-[#050510] to-[#000000]"></div>

         <svg width="300" height="200" className="absolute z-10">
            {/* Orbital Path */}
            <ellipse cx="150" cy="100" rx={orbitRadius} ry={orbitRadius * 0.4} fill="none" stroke="#334155" strokeWidth="1" strokeDasharray="4 4" />
            
            {/* Earth */}
            <circle cx="150" cy="100" r={earthRadius} fill="#0284c7" className="shadow-[0_0_30px_#0284c7]" />
            {/* Earth Glow */}
            <circle cx="150" cy="100" r={earthRadius + 5} fill="none" stroke="#bae6fd" strokeWidth="1" opacity="0.3" />

            {/* Satellite */}
            <g transform={`translate(${satX}, ${satY})`}>
               {/* Solar panels */}
               <rect x="-8" y="-2" width="16" height="4" fill="#3b82f6" />
               {/* Bus */}
               <rect x="-3" y="-3" width="6" height="6" fill="#f8fafc" />
            </g>
         </svg>
      </div>
      
      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Altitude: 400 km</span>
         <span>Velocity: <span className="text-emerald-400">7.67 km/s</span></span>
         <span>Inclination: 51.6°</span>
         <span>Debris Risk: <span className="text-emerald-400">Nominal</span></span>
      </div>
    </div>
  );
};
