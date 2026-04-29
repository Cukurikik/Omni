import React, { useState, useEffect } from 'react';

export const BraneCollision: React.FC = () => {
  const [distancePlanck, setDistancePlanck] = useState(10.0);
  const [energyDensity, setEnergyDensity] = useState(1e12); // GeV
  const [collisionThreat, setCollisionThreat] = useState(false);

  useEffect(() => {
    // Simulate Brane Dynamics in the Bulk
    const bulk = setInterval(() => {
       setDistancePlanck(prev => {
          // Branes slowly drift towards each other
          const next = prev - 0.2;
          
          if (next < 1.0) {
             setCollisionThreat(true);
             // Energy spikes as they near collision
             setEnergyDensity(1e19); 
          } else {
             setCollisionThreat(false);
             setEnergyDensity(1e12 / Math.max(0.1, next));
          }
          
          // Re-inflate/bounce back if they hit
          if (next <= 0) return 10.0;
          return next;
       });
    }, 200);

    return () => clearInterval(bulk);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-fuchsia-500">M-Theory Router</h2>
          <p className="text-xs text-slate-400">Inter-Brane Ekpyrotics</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-bold border ${collisionThreat ? 'bg-red-900/80 text-white border-red-500 shadow-[0_0_15px_#ef4444] animate-pulse' : 'bg-slate-800 text-fuchsia-400 border-slate-700'}`}>
          {collisionThreat ? 'EKPYROTIC BIG BANG IMMINENT' : 'BULK SPACE STABLE'}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex flex-col justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)] perspective-[600px]">
         
         {/* The 11D Bulk (Background) */}
         <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(217,70,239,0.1)_0%,transparent_100%)]"></div>

         {/* Universe A (Our Brane) */}
         <div 
            className="absolute w-full h-32 border-b-2 border-fuchsia-500 shadow-[0_10px_20px_rgba(217,70,239,0.3)] flex justify-center items-end pb-2"
            style={{ 
               transform: `translateY(-${Math.max(0, distancePlanck * 5)}px) rotateX(60deg)`,
               background: 'linear-gradient(to top, rgba(217,70,239,0.2), transparent)'
            }}
         >
            <span className="text-[10px] font-mono text-fuchsia-300">BRANE ALPHA (OUR UNIVERSE)</span>
         </div>

         {/* Universe B (Parallel Brane) */}
         <div 
            className="absolute w-full h-32 border-t-2 border-cyan-500 shadow-[0_-10px_20px_rgba(6,182,212,0.3)] flex justify-center items-start pt-2"
            style={{ 
               transform: `translateY(${Math.max(0, distancePlanck * 5)}px) rotateX(60deg)`,
               background: 'linear-gradient(to bottom, rgba(6,182,212,0.2), transparent)'
            }}
         >
            <span className="text-[10px] font-mono text-cyan-300">BRANE BETA (PARALLEL UNIVERSE)</span>
         </div>

         {/* Graviton Routing (Particles traversing the gap) */}
         {!collisionThreat && distancePlanck > 0 && (
            <div className="absolute inset-0 flex justify-center items-center pointer-events-none">
               {[...Array(5)].map((_, i) => (
                  <div 
                     key={i}
                     className="absolute w-1 h-1 bg-white rounded-full shadow-[0_0_10px_#fff]"
                     style={{
                        left: `${20 + Math.random() * 60}%`,
                        animation: `bounce-bulk ${0.5 + Math.random()}s linear infinite`
                     }}
                  ></div>
               ))}
            </div>
         )}
         
         {/* Collision Flash */}
         {distancePlanck <= 0 && (
            <div className="absolute inset-0 bg-white z-50 animate-[ping_0.2s_ease-out_forwards]"></div>
         )}
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Brane Separation</div>
            <div className={`text-lg font-mono font-bold ${collisionThreat ? 'text-red-400' : 'text-slate-300'}`}>
               {distancePlanck.toFixed(2)} <span className="text-xs text-slate-500">l_p</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Bulk Energy Density</div>
            <div className="text-lg font-mono font-bold text-fuchsia-400 truncate">
               {energyDensity > 1e15 ? `10^${Math.log10(energyDensity).toFixed(1)}` : energyDensity.toExponential(1)} <span className="text-[10px] text-slate-500">GeV</span>
            </div>
         </div>
      </div>

      <div className="w-full bg-slate-950 rounded border border-slate-800 p-2 text-[10px] font-mono text-center">
         <span className={collisionThreat ? 'text-red-400 font-bold' : 'text-emerald-400'}>
            {collisionThreat ? 'CRITICAL: BRANE INTERSECTION IN PROGRESS' : 'GRAVITON ROUTING TUNNEL SECURE'}
         </span>
      </div>

      <style>{`
        @keyframes bounce-bulk {
          0% { transform: translateY(-30px); opacity: 0; }
          50% { opacity: 1; }
          100% { transform: translateY(30px); opacity: 0; }
        }
      `}</style>
    </div>
  );
};
