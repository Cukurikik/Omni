import React, { useState, useEffect } from 'react';

export const InVivoNav: React.FC = () => {
  const [swarm, setSwarm] = useState<{id: number, x: number, y: number}[]>([]);
  const [pulse, setPulse] = useState(false);

  useEffect(() => {
    // Initialize swarm
    const initial = Array.from({length: 30}, (_, i) => ({
       id: i,
       x: 20 + Math.random() * 20,
       y: 40 + Math.random() * 20
    }));
    setSwarm(initial);

    // Heartbeat pulse effect (blood flow pushing them)
    const heart = setInterval(() => {
       setPulse(true);
       setTimeout(() => setPulse(false), 200);
       
       setSwarm(prev => prev.map(bot => ({
          ...bot,
          x: bot.x + 5 + Math.random() * 2, // Push right (flow)
          y: bot.y + (Math.random() - 0.5) * 4 // Brownian drift
       })));
    }, 1000); // 60 BPM

    return () => clearInterval(heart);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-rose-400">In-Vivo Nav</h2>
          <p className="text-xs text-slate-400">Nanobot Bloodstream Router</p>
        </div>
        <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_#10b981] animate-pulse"></div>
      </div>

      <div className={`bg-rose-950 p-4 rounded border-2 mb-4 h-[160px] relative overflow-hidden transition-colors duration-200 ${pulse ? 'border-rose-500/50 bg-rose-900' : 'border-rose-900'}`}>
         
         {/* Artery Walls */}
         <div className="absolute top-0 left-0 right-0 h-4 bg-rose-800/40 rounded-b-[50%] blur-sm"></div>
         <div className="absolute bottom-0 left-0 right-0 h-4 bg-rose-800/40 rounded-t-[50%] blur-sm"></div>

         {/* Target (Tumor site) */}
         <div className="absolute right-4 top-1/2 transform -translate-y-1/2 w-8 h-8 bg-purple-900/80 border border-purple-500/50 rounded-full flex items-center justify-center animate-pulse">
            <span className="text-[8px] font-mono text-purple-300">TARGET</span>
         </div>

         {/* White Blood Cell (Macrophage) */}
         <div className="absolute left-10 bottom-6 w-10 h-10 bg-slate-200/20 border border-white/30 rounded-full blur-[1px]"></div>
         <span className="absolute left-12 bottom-4 text-[8px] font-mono text-white/50">WBC</span>

         {/* The Nanobot Swarm */}
         {swarm.map((bot) => (
            <div 
               key={bot.id}
               className="absolute w-1.5 h-1 bg-cyan-400 rounded-sm shadow-[0_0_5px_#22d3ee] transition-all duration-300 ease-out"
               style={{ 
                  left: `${bot.x}%`, 
                  top: `${bot.y}%`,
                  opacity: bot.x > 90 ? 0 : 1 // Disappear when reaching target
               }}
            ></div>
         ))}
      </div>
      
      <div className="space-y-2 mb-4">
         <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400">MRI Steering Gradient</span>
            <span className="font-bold font-mono text-sky-400">2.4 T/m →</span>
         </div>
         {/* Blood Pressure/Flow Visualizer */}
         <div className="w-full h-1 bg-slate-800 rounded relative overflow-hidden">
            <div className={`absolute top-0 bottom-0 left-0 bg-rose-500 transition-all duration-100 ${pulse ? 'w-full' : 'w-1/3'}`}></div>
         </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Agents: <span className="text-white">1,048,576</span></span>
         <span>Stokes Drag: <span className="text-emerald-400">Compensated</span></span>
      </div>
    </div>
  );
};
