import React, { useState, useEffect } from 'react';

export const DagVisualizer: React.FC = () => {
  const [activeNode, setActiveNode] = useState<number>(0);

  // Deterministic DAG layout representing PyTensor Graph
  const nodes = [
    { id: 0, label: 'x', type: 'input', x: 20, y: 20 },
    { id: 1, label: 'W', type: 'weight', x: 20, y: 80 },
    { id: 2, label: 'Dot', type: 'op', x: 50, y: 50 },
    { id: 3, label: 'b', type: 'weight', x: 50, y: 80 },
    { id: 4, label: 'Add', type: 'op', x: 80, y: 50 },
  ];

  const edges = [
    { from: 0, to: 2 },
    { from: 1, to: 2 },
    { from: 2, to: 4 },
    { from: 3, to: 4 },
  ];

  useEffect(() => {
    // Animate execution flow deterministically
    const sequence = [0, 1, 2, 3, 4, -1];
    let idx = 0;
    
    const interval = setInterval(() => {
      idx = (idx + 1) % sequence.length;
      setActiveNode(sequence[idx]);
    }, 600);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-950 p-6 rounded-lg border border-slate-800 shadow-xl max-w-lg mx-auto font-sans relative overflow-hidden">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-teal-500">PyTensor DAG</h2>
        <p className="text-xs text-slate-400">Execution Flow Tracer</p>
      </div>

      <div className="relative w-full h-48 bg-slate-900 border border-slate-800 rounded">
        {/* Draw Edges */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none">
          {edges.map((e, i) => {
            const n1 = nodes.find(n => n.id === e.from)!;
            const n2 = nodes.find(n => n.id === e.to)!;
            const isActive = activeNode === e.to || activeNode === e.from;
            return (
              <line 
                key={i}
                x1={`${n1.x}%`} y1={`${n1.y}%`}
                x2={`${n2.x}%`} y2={`${n2.y}%`}
                stroke={isActive ? '#14b8a6' : '#334155'}
                strokeWidth={isActive ? 3 : 2}
                className="transition-all duration-300"
              />
            );
          })}
        </svg>

        {/* Draw Nodes */}
        {nodes.map(node => {
          const isActive = activeNode === node.id;
          const bg = node.type === 'op' ? 'bg-indigo-600' : 'bg-slate-700';
          return (
            <div 
              key={node.id}
              className={`absolute w-10 h-10 -ml-5 -mt-5 rounded-full flex items-center justify-center text-xs font-bold text-white border-2 shadow-lg transition-all duration-300
                ${bg} ${isActive ? 'border-teal-400 shadow-[0_0_15px_#2dd4bf] scale-125' : 'border-slate-800'}
              `}
              style={{ left: `${node.x}%`, top: `${node.y}%` }}
            >
              {node.label}
            </div>
          );
        })}
      </div>
    </div>
  );
};
