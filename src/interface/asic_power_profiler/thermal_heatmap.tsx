import React, { useState, useEffect } from 'react';

export const ThermalHeatmap: React.FC = () => {
  const [temps, setTemps] = useState<number[][]>([]);
  const gridSize = 8; // 8x8 ASIC cores

  useEffect(() => {
    // Initial cool state (40C)
    const initial = Array(gridSize).fill(0).map(() => Array(gridSize).fill(40));
    setTemps(initial);

    const interval = setInterval(() => {
      setTemps(prev => {
         const next = prev.map(row => [...row]);
         // Simulate heating up specific tensor cores
         for(let i = 0; i < 3; i++) {
            const x = Math.floor(Math.random() * gridSize);
            const y = Math.floor(Math.random() * gridSize);
            // Heat up by 5-15C, clamp to max 105C
            next[y][x] = Math.min(105, next[y][x] + (Math.random() * 10 + 5));
         }
         
         // Ambient cooling for all cells
         for(let y=0; y<gridSize; y++){
            for(let x=0; x<gridSize; x++){
               next[y][x] = Math.max(40, next[y][x] - 2);
            }
         }
         
         return next;
      });
    }, 250);
    return () => clearInterval(interval);
  }, []);

  // Helper to map temp (40-105) to a color (Blue -> Yellow -> Red)
  const getTempColor = (t: number) => {
     if (t < 60) return `rgb(56, 189, 248)`; // Sky blue (cool)
     if (t < 85) return `rgb(250, 204, 21)`;  // Yellow (warm)
     if (t < 95) return `rgb(249, 115, 22)`;  // Orange (hot)
     return `rgb(225, 29, 72)`;               // Rose (critical)
  };

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-red-500">ASIC Thermals</h2>
          <p className="text-xs text-slate-400">Silicon Die Heatmap</p>
        </div>
        <div className="px-2 py-1 bg-red-900/30 text-red-500 text-[10px] font-mono rounded border border-red-800">
          Max: {Math.max(...temps.flat() || [40]).toFixed(1)}°C
        </div>
      </div>

      <div className="bg-slate-950 p-2 rounded border border-slate-800 relative mb-4">
         <div className="grid grid-cols-8 gap-1">
            {temps.flat().map((t, i) => (
               <div 
                 key={i} 
                 className="aspect-square rounded-sm transition-colors duration-300"
                 style={{ 
                    backgroundColor: getTempColor(t),
                    opacity: 0.8 + (t/105)*0.2 // hotter = more opaque
                 }}
                 title={`${t.toFixed(1)}°C`}
               ></div>
            ))}
         </div>
         {/* Fake Processor Label */}
         <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-20 mix-blend-overlay">
            <span className="text-4xl font-bold tracking-widest rotate-[-30deg]">OMNI-LPU</span>
         </div>
      </div>
      
      <div className="flex justify-between items-center text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>TDP: 350W</span>
         <span>Cooling Fan: <span className="text-sky-400">4,200 RPM</span></span>
      </div>
    </div>
  );
};
