import React, { useState, useEffect } from 'react';

export const ComputationGraph: React.FC = () => {
  const [nodes, setNodes] = useState<{id: string, op: string, shape: string, active: boolean}[]>([]);

  useEffect(() => {
    // Deterministic static layout of a simple Neural Net computation graph
    const initialNodes = [
      { id: 'Input', op: 'TENSOR', shape: '[32, 784]', active: false },
      { id: 'W1', op: 'PARAM', shape: '[784, 128]', active: false },
      { id: 'MatMul1', op: 'MATMUL', shape: '[32, 128]', active: false },
      { id: 'ReLU1', op: 'RELU', shape: '[32, 128]', active: false },
      { id: 'W2', op: 'PARAM', shape: '[128, 10]', active: false },
      { id: 'MatMul2', op: 'MATMUL', shape: '[32, 10]', active: false },
      { id: 'CrossEnt', op: 'LOSS', shape: '[1]', active: false }
    ];
    
    setNodes(initialNodes);

    let step = 0;
    const interval = setInterval(() => {
      step++;
      
      // Simulate Forward pass then Backward pass
      // Forward: 0->6, Backward: 6->0
      const phase = Math.floor(step / 8) % 2; // 0 = forward, 1 = backward
      const activeIdx = phase === 0 ? step % 8 : 7 - (step % 8);

      setNodes(prev => prev.map((n, i) => ({
        ...n,
        active: i === activeIdx
      })));

    }, 300);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-zinc-950 p-6 rounded-lg border border-zinc-800 shadow-xl max-w-sm mx-auto font-sans">
      <div className="mb-4 border-b border-zinc-800 pb-2">
        <h2 className="text-xl font-bold text-rose-500">Autograd Graph</h2>
        <p className="text-xs text-zinc-500">DFDX Tensor Trace</p>
      </div>

      <div className="flex flex-col items-center space-y-2 py-4 relative">
        {/* Draw vertical connecting lines */}
        <div className="absolute top-8 bottom-8 w-px bg-zinc-800 -z-10"></div>

        {nodes.map((node) => (
          <div 
            key={node.id} 
            className={`w-full max-w-[200px] p-2 rounded flex justify-between items-center transition-all duration-200 border
              ${node.active ? 'bg-rose-900/40 border-rose-500 shadow-[0_0_10px_#f43f5e]' : 'bg-zinc-900 border-zinc-800'}
            `}
          >
            <div>
              <div className={`text-xs font-bold ${node.active ? 'text-rose-400' : 'text-zinc-300'}`}>{node.id}</div>
              <div className="text-[10px] text-zinc-500 font-mono">{node.op}</div>
            </div>
            <div className="text-[10px] bg-zinc-950 px-2 py-1 rounded border border-zinc-800 font-mono text-zinc-400">
              {node.shape}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
