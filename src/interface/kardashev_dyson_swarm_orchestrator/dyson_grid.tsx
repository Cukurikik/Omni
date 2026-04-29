import React, { useState, useEffect } from 'react';

export const DysonGrid: React.FC = () => {
  const [swarmYield, setSwarmYield] = useState(384.6); // Yottawatts (Sun's output)
  const [sailsCount, setSailsCount] = useState(45.2); // Billions
  const [efficiency, setEfficiency] = useState(85.5);

  useEffect(() => {
    // Simulate swarm construction and yield fluctuations
    const construct = setInterval(() => {
      setSailsCount(prev => prev + 0.01);
      setSwarmYield(prev => prev + (Math.random() - 0.4) * 0.5);
      setEfficiency(prev => prev + (Math.random() - 0.5) * 0.1);
    }, 100);

    return () => clearInterval(construct);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-yellow-500">Dyson Swarm</h2>
          <p className="text-xs text-slate-400">Kardashev Type-II Grid</p>
        </div>
        <div className="px-2 py-1 rounded text-[10px] font-mono border bg-yellow-900/30 text-yellow-400 border-yellow-800 animate-pulse">
          HARVESTING YOTTAWATTS
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] flex items-center justify-center relative overflow-hidden">
         {/* Deep Space Background */}
         <div className="absolute inset-0">
            {[...Array(50)].map((_, i) => (
               <div 
                  key={i} 
                  className="absolute bg-white rounded-full opacity-50"
                  style={{
                     width: Math.random() * 2 + 'px',
                     height: Math.random() * 2 + 'px',
                     top: Math.random() * 100 + '%',
                     left: Math.random() * 100 + '%'
                  }}
               ></div>
            ))}
         </div>

         {/* The Star */}
         <div className="w-16 h-16 bg-gradient-to-tr from-orange-600 to-yellow-300 rounded-full shadow-[0_0_50px_#facc15] relative z-10 flex items-center justify-center animate-pulse">
            <div className="w-full h-full rounded-full border-2 border-orange-400/50 scale-110"></div>
         </div>

         {/* The Swarm (Orbiting rings of mirrors) */}
         <div className="absolute w-40 h-40 border border-yellow-500/20 rounded-full animate-[spin_10s_linear_infinite]">
            {[...Array(12)].map((_, i) => (
               <div key={i} className="w-2 h-2 bg-slate-300 absolute top-0 left-1/2 transform -translate-x-1/2 shadow-[0_0_5px_#fff]" style={{ transform: `rotate(${i * 30}deg) translateY(-20px)` }}></div>
            ))}
         </div>
         
         <div className="absolute w-64 h-64 border border-orange-500/10 rounded-full animate-[spin_15s_linear_infinite_reverse]">
            {[...Array(24)].map((_, i) => (
               <div key={i} className="w-1 h-1 bg-slate-400 absolute top-0 left-1/2 transform -translate-x-1/2" style={{ transform: `rotate(${i * 15}deg) translateY(-32px)` }}></div>
            ))}
         </div>
         
         {/* Microwave Energy Beams to Earth */}
         <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-full h-px bg-yellow-400/30 transform rotate-45 shadow-[0_0_10px_#facc15]"></div>
            <div className="w-full h-px bg-yellow-400/30 transform -rotate-45 shadow-[0_0_10px_#facc15]"></div>
         </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Total Yield</div>
            <div className="text-lg font-mono font-bold text-yellow-400">{swarmYield.toFixed(2)} <span className="text-xs">YW</span></div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Active Statites</div>
            <div className="text-lg font-mono font-bold text-sky-400">{sailsCount.toFixed(2)} <span className="text-xs">Billion</span></div>
         </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Capture Eff: <span className="text-emerald-400">{efficiency.toFixed(1)}%</span></span>
         <span>Collision Mesh: <span className="text-emerald-400">Stable</span></span>
      </div>
    </div>
  );
};
