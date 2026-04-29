import React, { useState, useEffect } from 'react';

export const CosmicStringLensing: React.FC = () => {
  const [stringX, setStringX] = useState(0);
  const [lensingAngle, setLensingAngle] = useState(3.1); // arcseconds

  useEffect(() => {
    // Simulate Cosmic String moving across the background star field
    const motion = setInterval(() => {
       setStringX(prev => {
          const next = prev + 1;
          return next > 150 ? -50 : next; // Reset
       });
    }, 50);

    return () => clearInterval(motion);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-indigo-400">Cosmic String</h2>
          <p className="text-xs text-slate-400">Topological Defect</p>
        </div>
        <div className="px-2 py-1 rounded text-[10px] font-mono border bg-indigo-900/30 text-indigo-400 border-indigo-800 animate-pulse">
          MICROLENSING
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex items-center justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* Background Star Field */}
         <div className="absolute inset-0">
            {[...Array(50)].map((_, i) => {
               // A specific target star in the center
               const isTarget = i === 0;
               const x = isTarget ? 50 : Math.random() * 100;
               const y = isTarget ? 50 : Math.random() * 100;
               
               // Calculate gravitational lensing effect
               // If the string passes over the star, it creates a duplicate
               let dx = stringX - x;
               const isLensed = Math.abs(dx) < 10 && !isTarget;
               const targetLensed = isTarget && Math.abs(dx) < 15;
               
               return (
                  <React.Fragment key={i}>
                     <div 
                        className={`absolute rounded-full ${isTarget ? 'w-2 h-2 bg-yellow-400 shadow-[0_0_10px_#facc15]' : 'w-1 h-1 bg-white'}`}
                        style={{ 
                           left: `${isTarget && targetLensed ? x - 5 : x}%`, 
                           top: `${y}%`,
                           opacity: targetLensed ? 0.8 : 1
                        }}
                     ></div>
                     
                     {/* The double image created by the conical spacetime deficit */}
                     {(isLensed || targetLensed) && (
                        <div 
                           className={`absolute rounded-full ${isTarget ? 'w-2 h-2 bg-yellow-400 shadow-[0_0_10px_#facc15]' : 'w-1 h-1 bg-white'}`}
                           style={{ 
                              left: `${isTarget && targetLensed ? x + 5 : x + 8}%`, 
                              top: `${y}%`,
                              opacity: 0.8
                           }}
                        ></div>
                     )}
                  </React.Fragment>
               )
            })}
         </div>

         {/* The Cosmic String (Technically invisible, but rendered here for viz) */}
         <div 
            className="absolute top-0 bottom-0 w-[2px] bg-indigo-500/50 shadow-[0_0_15px_#6366f1] blur-[1px]"
            style={{ left: `${stringX}%` }}
         ></div>
         
         {/* Spacetime conical deficit distortion effect */}
         <div 
            className="absolute top-0 bottom-0 w-20 pointer-events-none"
            style={{ 
               left: `${stringX - 10}%`,
               background: 'linear-gradient(90deg, rgba(0,0,0,0) 0%, rgba(99,102,241,0.1) 50%, rgba(0,0,0,0) 100%)',
               backdropFilter: 'hue-rotate(90deg)'
            }}
         ></div>
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Deficit Angle</div>
            <div className="text-lg font-mono font-bold text-sky-400">{lensingAngle.toFixed(1)} <span className="text-xs">arcsec</span></div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Mass Density</div>
            <div className="text-lg font-mono font-bold text-white">10²⁰ <span className="text-xs">kg/m</span></div>
         </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded text-center">
         <span className="col-span-2">Origin: <span className="text-emerald-400">Kibble Phase Transition</span></span>
      </div>
    </div>
  );
};
