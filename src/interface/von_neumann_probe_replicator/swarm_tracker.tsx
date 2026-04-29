import React, { useState, useEffect } from 'react';

export const SwarmTracker: React.FC = () => {
  const [probeCount, setProbeCount] = useState(1);
  const [massConsumed, setMassConsumed] = useState(0.5); // Tons
  const [greyGooAlert, setGreyGooAlert] = useState(false);
  const [swarm, setSwarm] = useState<{x: number, y: number, vx: number, vy: number}[]>([]);

  useEffect(() => {
    // Initial probe
    setSwarm([{x: 50, y: 50, vx: 1, vy: -1}]);
  }, []);

  useEffect(() => {
    // Simulate Exponential Replication
    const replication = setInterval(() => {
       if (probeCount < 2048) {
          setProbeCount(prev => prev * 2);
          setMassConsumed(prev => prev * 2);
          
          // Add visually to the swarm
          setSwarm(prev => {
             const newSwarm = [...prev];
             // Add copies near existing probes
             prev.forEach(p => {
                if (newSwarm.length < 200) { // Limit DOM nodes
                   newSwarm.push({
                      x: p.x + (Math.random() - 0.5) * 10,
                      y: p.y + (Math.random() - 0.5) * 10,
                      vx: (Math.random() - 0.5) * 2,
                      vy: (Math.random() - 0.5) * 2
                   });
                }
             });
             return newSwarm;
          });
       } else {
          setGreyGooAlert(true);
       }
    }, 1500);

    return () => clearInterval(replication);
  }, [probeCount]);

  useEffect(() => {
    // Boids-like movement logic
    const move = setInterval(() => {
       setSwarm(prev => prev.map(p => {
          let nx = p.x + p.vx;
          let ny = p.y + p.vy;
          let nvx = p.vx;
          let nvy = p.vy;

          // Bounce off walls
          if (nx <= 0 || nx >= 100) nvx *= -1;
          if (ny <= 0 || ny >= 100) nvy *= -1;

          return { x: nx, y: ny, vx: nvx, vy: nvy };
       }));
    }, 50);

    return () => clearInterval(move);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-orange-500">Von Neumann Swarm</h2>
          <p className="text-xs text-slate-400">Self-Replicating Automata</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-bold border ${greyGooAlert ? 'bg-red-900/80 text-white border-red-500 shadow-[0_0_15px_#ef4444] animate-pulse' : 'bg-slate-800 text-slate-400 border-slate-700'}`}>
          {greyGooAlert ? 'GREY GOO EVENT' : 'REPLICATING'}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* The Asteroid (being consumed) */}
         <div 
            className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-stone-700 rounded-full shadow-[inset_-10px_-10px_20px_#1c1917] transition-all duration-1000"
            style={{ 
               width: `${Math.max(0, 150 - (probeCount / 10))}px`, 
               height: `${Math.max(0, 150 - (probeCount / 10))}px`,
               opacity: greyGooAlert ? 0 : 1
            }}
         >
            {/* Craters */}
            <div className="absolute top-4 left-4 w-6 h-6 bg-stone-800 rounded-full shadow-[inset_2px_2px_5px_#000]"></div>
            <div className="absolute bottom-8 right-6 w-10 h-10 bg-stone-800 rounded-full shadow-[inset_2px_2px_5px_#000]"></div>
         </div>

         {/* The Swarm */}
         {swarm.map((probe, i) => (
            <div 
               key={i}
               className={`absolute w-1.5 h-1.5 bg-orange-400 rounded-sm shadow-[0_0_5px_#f97316] ${greyGooAlert ? 'animate-pulse bg-red-500 shadow-[0_0_5px_#ef4444]' : ''}`}
               style={{ 
                  left: `${probe.x}%`, 
                  top: `${probe.y}%`,
                  transform: `rotate(${Math.atan2(probe.vy, probe.vx)}rad)`
               }}
            ></div>
         ))}
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Probe Population</div>
            <div className={`text-lg font-mono font-bold ${greyGooAlert ? 'text-red-400' : 'text-orange-400'}`}>
               {probeCount.toLocaleString()}
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Mass Consumed</div>
            <div className="text-lg font-mono font-bold text-slate-300">
               {massConsumed > 1000 ? (massConsumed/1000).toFixed(1) + 'k' : massConsumed} <span className="text-xs text-slate-500">Tons</span>
            </div>
         </div>
      </div>

      <div className="w-full bg-slate-950 rounded border border-slate-800 p-2 text-[10px] font-mono text-center">
         <span className={greyGooAlert ? 'text-red-400' : 'text-emerald-400'}>
            {greyGooAlert ? 'ASTEROID COMPLETELY DISASSEMBLED' : 'MINING AND PRINTING CHASSIS'}
         </span>
      </div>
    </div>
  );
};
