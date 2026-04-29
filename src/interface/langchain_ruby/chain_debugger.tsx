import React, { useState, useEffect } from 'react';

export const ChainDebugger: React.FC = () => {
  const [nodes, setNodes] = useState<{id: string, state: string, memory: number}[]>([]);

  useEffect(() => {
    let t = 0;
    const interval = setInterval(() => {
      t++;
      // Deterministic node chain state visualization
      setNodes([
        { id: 'Prompt_Template', state: t % 10 < 3 ? 'Active' : 'Idle', memory: 12 },
        { id: 'LLM_Interface', state: t % 10 >= 3 && t % 10 < 7 ? 'Active' : 'Idle', memory: 256 },
        { id: 'Output_Parser', state: t % 10 >= 7 ? 'Active' : 'Idle', memory: 8 }
      ]);
    }, 500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-neutral-900 p-6 rounded-lg border border-neutral-700 font-sans max-w-xl mx-auto shadow-2xl">
      <div className="border-b border-neutral-800 pb-4 mb-4">
        <h2 className="text-xl font-bold text-red-400">Langchain Ruby Debugger</h2>
        <p className="text-xs text-neutral-500">Execution DAG Trace</p>
      </div>

      <div className="space-y-4 relative">
        <div className="absolute left-8 top-4 bottom-4 w-1 bg-neutral-800 z-0"></div>
        
        {nodes.map((node, i) => (
          <div key={node.id} className="relative z-10 flex items-center gap-6">
            <div className={`w-16 h-16 rounded-full border-4 flex items-center justify-center transition-colors duration-300 bg-neutral-900 ${node.state === 'Active' ? 'border-red-500 shadow-[0_0_15px_#ef4444]' : 'border-neutral-700'}`}>
              <span className="text-neutral-400 font-mono text-sm">{i+1}</span>
            </div>
            
            <div className={`flex-1 p-4 rounded border transition-colors duration-300 ${node.state === 'Active' ? 'bg-neutral-800 border-red-500/50' : 'bg-neutral-950 border-neutral-800'}`}>
              <h3 className="text-neutral-200 font-semibold">{node.id.replace('_', ' ')}</h3>
              <div className="flex justify-between mt-2 text-xs font-mono">
                <span className={node.state === 'Active' ? 'text-red-400' : 'text-neutral-500'}>Status: {node.state}</span>
                <span className="text-blue-400">Mem: {node.memory} MB</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
