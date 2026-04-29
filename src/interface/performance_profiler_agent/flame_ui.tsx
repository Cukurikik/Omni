import React, { useState, useEffect } from 'react';

export const FlameUI: React.FC = () => {
  const [hovered, setHovered] = useState<string | null>(null);

  // Simulated Flame Graph data
  const graph = [
    { id: 'main', width: '100%', color: 'bg-orange-600', name: 'main()', time: '120ms' },
    { id: 'req', width: '90%', color: 'bg-orange-500', name: 'handle_request()', time: '108ms', ml: '5%' },
    { id: 'db', width: '60%', color: 'bg-red-500', name: 'db_query()', time: '72ms', ml: '5%' },
    { id: 'json', width: '25%', color: 'bg-amber-500', name: 'json_parse()', time: '30ms', ml: '70%' },
    { id: 'tcp', width: '55%', color: 'bg-red-600', name: 'tcp_wait()', time: '66ms', ml: '5%' },
  ];

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 border-b border-slate-700 pb-2">
        <h2 className="text-xl font-bold text-orange-400">Flame Graph</h2>
        <p className="text-xs text-slate-400">CPU Bottleneck Analysis</p>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 text-xs font-mono relative overflow-hidden flex flex-col-reverse gap-1 h-[160px]">
         {graph.map((node) => (
            <div 
               key={node.id}
               className={`${node.color} h-6 rounded cursor-pointer transition-all duration-200 flex items-center px-2 overflow-hidden border border-black/20 ${hovered === node.id ? 'brightness-125 scale-y-110' : 'hover:brightness-110'}`}
               style={{ width: node.width, marginLeft: node.ml || '0' }}
               onMouseEnter={() => setHovered(node.id)}
               onMouseLeave={() => setHovered(null)}
            >
               <span className="text-[10px] text-white truncate drop-shadow-md">
                 {node.name} {hovered === node.id && `(${node.time})`}
               </span>
            </div>
         ))}
      </div>
      
      <div className="mt-4 p-3 bg-rose-950/30 border border-rose-900/50 rounded flex gap-3 items-center">
         <div className="text-2xl">🔥</div>
         <div>
            <div className="text-[10px] uppercase font-bold text-rose-400 mb-0.5">Critical Bottleneck</div>
            <div className="text-xs text-slate-300">
               <span className="font-mono text-white">tcp_wait()</span> consumes 55% of total CPU cycles. Consider async I/O.
            </div>
         </div>
      </div>
    </div>
  );
};
