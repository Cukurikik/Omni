import React, { useState, useEffect } from 'react';

export const MicrogravitySlosh: React.FC = () => {
  const [fluidLevel, setFluidLevel] = useState(50);
  const [sloshAngle, setSloshAngle] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate zero-g fluid sloshing due to a small RCS thruster impulse
      setSloshAngle(prev => {
         const newAngle = Math.sin(Date.now() / 500) * 15; // +/- 15 degrees of slosh
         return newAngle;
      });
      // Capillary action slowly pulling fluid up the walls
      setFluidLevel(prev => Math.min(80, prev + 0.1));
    }, 50);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-cyan-400">Fluid Dynamics</h2>
          <p className="text-xs text-slate-400">Zero-G Tank Slosh</p>
        </div>
        <div className="text-[10px] font-mono bg-cyan-900/30 text-cyan-400 border border-cyan-800 px-2 py-1 rounded">
          Navier-Stokes SPH
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 relative h-[200px] mb-4 flex items-center justify-center">
         
         {/* Satellite Propellant Tank */}
         <div className="w-32 h-40 border-4 border-slate-500 rounded-full relative overflow-hidden bg-slate-800/20">
            
            {/* The Fluid in Zero-G (sloshing and creeping up walls via capillary action) */}
            <div 
               className="absolute bottom-0 w-[150%] h-full bg-cyan-500/80 -left-[25%] origin-bottom transition-transform duration-75 ease-linear"
               style={{ 
                  height: `${fluidLevel}%`,
                  transform: `rotate(${sloshAngle}deg)`,
                  borderRadius: '100% 100% 0 0 / 20% 20% 0 0' // Curved meniscus
               }}
            >
               {/* Internal bubbles/particles */}
               <div className="absolute top-2 left-4 w-2 h-2 rounded-full bg-white/30"></div>
               <div className="absolute top-4 right-8 w-1 h-1 rounded-full bg-white/40"></div>
            </div>
            
            {/* Center Intake Pipe (PMD - Propellant Management Device) */}
            <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-2 h-20 bg-slate-400 border-l border-slate-300"></div>
         </div>

      </div>
      
      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Capillary Pressure: <span className="text-white">1.2 Pa</span></span>
         <span>Tank Vol: <span className="text-cyan-400 font-bold">{fluidLevel.toFixed(1)}%</span></span>
         <span className="col-span-2 text-cyan-400">Intake Status: <span className="text-emerald-400 font-bold">WETTED (Safe to Fire)</span></span>
      </div>
    </div>
  );
};
