import React, { useState, useEffect } from 'react';

// Boids Agent definition
interface Agent {
  id: number;
  x: number;
  y: number;
  vx: number;
  vy: number;
}

export const SwarmViz: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const numAgents = 30;

  useEffect(() => {
    // Initialize random swarm
    const initAgents: Agent[] = [];
    for (let i = 0; i < numAgents; i++) {
      initAgents.push({
        id: i,
        x: Math.random() * 200 + 50,
        y: Math.random() * 100 + 50,
        vx: (Math.random() - 0.5) * 4,
        vy: (Math.random() - 0.5) * 4
      });
    }
    setAgents(initAgents);

    const interval = setInterval(() => {
      setAgents(prev => {
        return prev.map(agent => {
          // Simplified flocking for UI rendering
          let cohX = 0, cohY = 0, sepX = 0, sepY = 0, alignX = 0, alignY = 0;
          let count = 0;

          for (const other of prev) {
            if (other.id === agent.id) continue;
            const dx = other.x - agent.x;
            const dy = other.y - agent.y;
            const dist = Math.sqrt(dx*dx + dy*dy);

            if (dist < 40) { // Sight radius
              cohX += other.x; cohY += other.y;
              alignX += other.vx; alignY += other.vy;
              if (dist < 15) { // Separation radius
                sepX -= dx; sepY -= dy;
              }
              count++;
            }
          }

          let nvx = agent.vx;
          let nvy = agent.vy;

          if (count > 0) {
            cohX = (cohX / count - agent.x) * 0.05;
            cohY = (cohY / count - agent.y) * 0.05;
            alignX = (alignX / count - agent.vx) * 0.05;
            alignY = (alignY / count - agent.vy) * 0.05;
            
            nvx += cohX + alignX + sepX * 0.1;
            nvy += cohY + alignY + sepY * 0.1;
          }

          // Bounds checking (wrap around)
          let nx = agent.x + nvx;
          let ny = agent.y + nvy;
          if (nx < 0) nx = 300; if (nx > 300) nx = 0;
          if (ny < 0) ny = 200; if (ny > 200) ny = 0;

          // Limit speed
          const speed = Math.sqrt(nvx*nvx + nvy*nvy);
          if (speed > 4) { nvx = (nvx/speed)*4; nvy = (nvy/speed)*4; }

          return { ...agent, x: nx, y: ny, vx: nvx, vy: nvy };
        });
      });
    }, 50);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-indigo-400">Swarm Robotics</h2>
          <p className="text-xs text-slate-400">Decentralized Boids Consensus</p>
        </div>
        <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_#10b981] animate-pulse"></div>
      </div>

      <div className="bg-[#050510] p-0 rounded border border-slate-800 relative h-[200px] mb-4 overflow-hidden">
         <svg width="100%" height="100%" viewBox="0 0 300 200">
            {agents.map(agent => {
               // Calculate rotation based on velocity
               const angle = Math.atan2(agent.vy, agent.vx) * (180 / Math.PI);
               return (
                  <g key={agent.id} transform={`translate(${agent.x}, ${agent.y}) rotate(${angle})`}>
                     <polygon points="6,0 -4,-4 -4,4" fill="#818cf8" stroke="#4f46e5" strokeWidth="1" />
                  </g>
               );
            })}
         </svg>
      </div>
      
      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Agents: {numAgents}</span>
         <span>RF Mesh: <span className="text-emerald-400">99.9% Sync</span></span>
         <span className="col-span-2 text-indigo-400 font-bold">Rule: Separation + Alignment + Cohesion</span>
      </div>
    </div>
  );
};
