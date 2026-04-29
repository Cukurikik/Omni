import React, { useState, useEffect } from 'react';

export const TpuPodVisualizer: React.FC = () => {
  const [activeLinks, setActiveLinks] = useState<number[]>([]);

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate high-speed 3D Torus routing traffic
      const links = Array.from({ length: 8 }).map(() => Math.floor(Math.random() * 24));
      setActiveLinks(links);
    }, 150);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-blue-400">TPU Pod</h2>
          <p className="text-xs text-slate-400">3D Torus Topology</p>
        </div>
        <div className="text-[10px] font-mono bg-blue-900/50 text-blue-400 border border-blue-800 px-2 py-1 rounded">
           ICI: 600 GB/s
        </div>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 h-[180px] relative overflow-hidden perspective-1000 mb-4 flex items-center justify-center">
         <div className="grid grid-cols-4 gap-2 transform rotate-x-12 rotate-y-[-10deg]">
            {/* 16 TPU Cores in a slice */}
            {Array.from({ length: 16 }).map((_, i) => {
               const isActive = activeLinks.includes(i);
               return (
                  <div 
                    key={i} 
                    className={`w-8 h-8 border flex items-center justify-center transition-all duration-75 relative
                      ${isActive ? 'bg-blue-500 border-blue-300 shadow-[0_0_15px_#3b82f6] z-10 scale-110' : 'bg-slate-800 border-slate-600'}
                    `}
                  >
                     <div className={`w-2 h-2 rounded-full ${isActive ? 'bg-white' : 'bg-slate-600'}`}></div>
                     {/* Simulated Torus wrap-around links */}
                     {i < 12 && <div className="absolute top-8 left-4 w-px h-2 bg-blue-500/30"></div>}
                     {i % 4 !== 3 && <div className="absolute top-4 left-8 w-2 h-px bg-blue-500/30"></div>}
                  </div>
               );
            })}
         </div>
      </div>
      
      <div className="flex justify-between text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Slice: <span className="text-white font-bold">v4-16</span></span>
         <span>XLA Graph: <span className="text-emerald-400">Fused</span></span>
         <span>Bfloat16: <span className="text-blue-400">Active</span></span>
      </div>
    </div>
  );
};
