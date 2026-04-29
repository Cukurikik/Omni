import React, { useState, useEffect } from 'react';

export const EdgeTopology: React.FC = () => {
  const [activeNodes, setActiveNodes] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveNodes(prev => (prev < 12 ? prev + 1 : prev));
    }, 200);
    return () => clearInterval(interval);
  }, []);

  // Generate nodes around a central hub
  const nodes = Array.from({ length: 12 }).map((_, i) => {
    const angle = (i / 12) * Math.PI * 2;
    const r = 40; // radius %
    return {
      x: 50 + r * Math.cos(angle),
      y: 50 + r * Math.sin(angle),
      active: i < activeNodes,
      ping: Math.floor(Math.random() * 15 + 5)
    };
  });

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-sky-400">Edge Router</h2>
        <p className="text-xs text-slate-400">Low-Latency Topology</p>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 h-[200px] relative overflow-hidden">
         {/* Central Cloud Node */}
         <div className="absolute top-[50%] left-[50%] transform -translate-x-1/2 -translate-y-1/2 w-12 h-12 bg-sky-900 rounded-full border-2 border-sky-500 flex items-center justify-center z-20 shadow-[0_0_20px_#0ea5e9]">
             <span className="text-xl">☁️</span>
         </div>
         
         {/* Edge Nodes and Connections */}
         {nodes.map((node, i) => (
           <React.Fragment key={i}>
              {/* Connection Line */}
              <svg className="absolute inset-0 w-full h-full pointer-events-none z-0">
                 <line 
                   x1="50%" y1="50%" 
                   x2={`${node.x}%`} y2={`${node.y}%`} 
                   stroke={node.active ? '#0ea5e9' : '#334155'} 
                   strokeWidth="1" 
                   strokeDasharray={node.active ? "none" : "4"}
                   className={node.active ? "animate-pulse" : ""}
                 />
              </svg>
              
              {/* Node Point */}
              <div 
                 className={`absolute transform -translate-x-1/2 -translate-y-1/2 w-4 h-4 rounded-full border-2 z-10 transition-colors duration-500
                   ${node.active ? 'bg-sky-500 border-sky-300 shadow-[0_0_10px_#38bdf8]' : 'bg-slate-800 border-slate-600'}
                 `}
                 style={{ top: `${node.y}%`, left: `${node.x}%` }}
              >
                 {node.active && (
                    <div className="absolute -top-4 left-4 text-[8px] font-mono text-sky-300 whitespace-nowrap">
                       {node.ping}ms
                    </div>
                 )}
              </div>
           </React.Fragment>
         ))}
      </div>
      
      <div className="mt-3 flex justify-between text-xs text-slate-500 font-mono">
         <span>Edge Nodes: {activeNodes}/12</span>
         <span>Global Latency: <span className="text-emerald-400">~12ms</span></span>
      </div>
    </div>
  );
};
