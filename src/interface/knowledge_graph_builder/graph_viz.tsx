import React, { useState, useEffect } from 'react';

export const GraphViz: React.FC = () => {
  const [nodes, setNodes] = useState([{id: 'N0', label: 'Omni Framework', type: 'CORE'}]);
  const [edges, setEdges] = useState<{source: string, target: string, label: string}[]>([]);

  useEffect(() => {
    let step = 0;
    const interval = setInterval(() => {
      step++;
      if (step === 1) {
        setNodes(n => [...n, {id: 'N1', label: 'Agentic RAG', type: 'FEATURE'}]);
        setEdges(e => [...e, {source: 'N0', target: 'N1', label: 'IMPLEMENTS'}]);
      } else if (step === 2) {
        setNodes(n => [...n, {id: 'N2', label: 'LLVM', type: 'DEP'}]);
        setEdges(e => [...e, {source: 'N0', target: 'N2', label: 'COMPILES_VIA'}]);
      } else if (step === 3) {
        setNodes(n => [...n, {id: 'N3', label: 'Knowledge Graph', type: 'FEATURE'}]);
        setEdges(e => [...e, {source: 'N1', target: 'N3', label: 'UTILIZES'}]);
        clearInterval(interval);
      }
    }, 800);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-indigo-400">Graph RAG</h2>
          <p className="text-xs text-slate-400">Knowledge Triplet Extraction</p>
        </div>
        <div className="flex gap-1">
           <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-ping"></div>
        </div>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 h-[200px] relative overflow-hidden flex items-center justify-center">
         {/* Simplified representation of a force-directed graph UI */}
         <div className="absolute inset-0 opacity-10" style={{
            backgroundImage: 'radial-gradient(circle at center, #6366f1 1px, transparent 1px)',
            backgroundSize: '20px 20px'
         }}></div>
         
         <div className="relative z-10 w-full h-full">
            {nodes.map((node, i) => (
               <div 
                 key={node.id} 
                 className={`absolute transform -translate-x-1/2 -translate-y-1/2 rounded-full px-2 py-1 text-[10px] font-bold border whitespace-nowrap shadow-lg animate-fade-in
                   ${node.type === 'CORE' ? 'bg-indigo-900 text-indigo-200 border-indigo-500 top-1/2 left-1/2' : ''}
                   ${node.type === 'FEATURE' && i === 1 ? 'bg-emerald-900 text-emerald-200 border-emerald-500 top-1/4 left-3/4' : ''}
                   ${node.type === 'FEATURE' && i === 3 ? 'bg-amber-900 text-amber-200 border-amber-500 top-3/4 left-3/4' : ''}
                   ${node.type === 'DEP' ? 'bg-rose-900 text-rose-200 border-rose-500 top-3/4 left-1/4' : ''}
                 `}
               >
                 {node.label}
               </div>
            ))}
            
            {/* Edge labels simulated */}
            {edges.length > 0 && <div className="absolute top-[35%] left-[62%] text-[8px] text-slate-500 transform rotate-[25deg]">{edges[0].label}</div>}
            {edges.length > 1 && <div className="absolute top-[65%] left-[37%] text-[8px] text-slate-500 transform -rotate-[25deg]">{edges[1].label}</div>}
            {edges.length > 2 && <div className="absolute top-[50%] left-[75%] text-[8px] text-slate-500 transform rotate-90">{edges[2].label}</div>}
         </div>
      </div>
      
      <div className="mt-3 flex justify-between text-[10px] text-slate-500">
         <span>Entities: {nodes.length}</span>
         <span>Relations: {edges.length}</span>
      </div>
    </div>
  );
};
