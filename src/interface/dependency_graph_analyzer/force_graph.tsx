import React, { useState, useEffect } from 'react';

export const ForceGraph: React.FC = () => {
  const [nodes, setNodes] = useState([{id: 'omni-core', x: 50, y: 50, status: 'ok'}]);

  useEffect(() => {
    // Simulate async dependency resolution populating the graph
    let step = 0;
    const interval = setInterval(() => {
      step++;
      if (step === 1) {
        setNodes(n => [...n, {id: 'omni-net', x: 20, y: 70, status: 'ok'}]);
      } else if (step === 2) {
        setNodes(n => [...n, {id: 'omni-crypto', x: 80, y: 70, status: 'ok'}]);
      } else if (step === 3) {
        setNodes(n => [...n, {id: 'legacy-lib', x: 50, y: 90, status: 'conflict'}]);
        clearInterval(interval);
      }
    }, 800);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 border-b border-slate-700 pb-2">
        <h2 className="text-xl font-bold text-blue-400">Dependency Graph</h2>
        <p className="text-xs text-slate-400">Topological Package Resolution</p>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 h-[200px] relative overflow-hidden flex items-center justify-center">
         <div className="absolute w-full h-full">
            {/* Edges */}
            {nodes.length > 1 && <svg className="absolute inset-0 w-full h-full pointer-events-none z-0">
               <line x1="50%" y1="50%" x2="20%" y2="70%" stroke="#3b82f6" strokeWidth="2" strokeDasharray="4" className="animate-pulse" />
               {nodes.length > 2 && <line x1="50%" y1="50%" x2="80%" y2="70%" stroke="#3b82f6" strokeWidth="2" />}
               {nodes.length > 3 && <line x1="20%" y1="70%" x2="50%" y2="90%" stroke="#ef4444" strokeWidth="2" />}
            </svg>}

            {/* Nodes */}
            {nodes.map(node => (
               <div 
                 key={node.id} 
                 className={`absolute transform -translate-x-1/2 -translate-y-1/2 rounded-full px-2 py-1 text-[10px] font-bold border whitespace-nowrap shadow-lg animate-fade-in z-10
                   ${node.status === 'ok' ? 'bg-blue-900 text-blue-200 border-blue-500' : 'bg-rose-900 text-rose-200 border-rose-500 shadow-[0_0_15px_rgba(225,29,72,0.5)]'}
                 `}
                 style={{ top: \`\${node.y}%\`, left: \`\${node.x}%\` }}
               >
                 {node.id}
               </div>
            ))}
         </div>
      </div>
      
      <div className="mt-3 flex justify-between text-[10px] text-slate-500">
         <span>Resolved: {nodes.length - (nodes.length > 3 ? 1 : 0)}</span>
         <span>Conflicts: {nodes.length > 3 ? <span className="text-rose-400 font-bold">1 Detected</span> : '0'}</span>
      </div>
    </div>
  );
};
