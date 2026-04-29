import React, { useState, useEffect } from 'react';

export const KnowledgeGraphViz: React.FC = () => {
  const [nodes, setNodes] = useState<{id: number, x: number, y: number, r: number, active: boolean}[]>([]);
  const [edges, setEdges] = useState<{source: number, target: number}[]>([]);

  useEffect(() => {
    // Generate random clustered graph
    const newNodes = [];
    for (let i = 0; i < 30; i++) {
      const cluster = i % 3;
      newNodes.push({
        id: i,
        x: 50 + (cluster * 80) + (Math.random() * 40 - 20),
        y: 80 + (Math.random() * 60 - 30),
        r: Math.random() * 4 + 2,
        active: false
      });
    }
    
    const newEdges = [];
    for (let i = 0; i < 40; i++) {
      newEdges.push({
        source: Math.floor(Math.random() * 30),
        target: Math.floor(Math.random() * 30)
      });
    }

    setNodes(newNodes);
    setEdges(newEdges);

    // Simulate Graph RAG traversal
    let step = 0;
    const interval = setInterval(() => {
      setNodes(prev => prev.map(n => ({
        ...n,
        active: (n.id % 5) === (step % 5) || n.active
      })));
      step++;
      if (step > 10) clearInterval(interval);
    }, 400);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-fuchsia-400">Graph RAG</h2>
        <p className="text-xs text-slate-400">Knowledge Community Retrieval</p>
      </div>

      <div className="relative h-48 bg-slate-950 p-2 rounded border border-slate-800 overflow-hidden">
        <svg width="100%" height="100%" viewBox="0 0 300 160">
          {edges.map((e, i) => {
            const src = nodes[e.source];
            const tgt = nodes[e.target];
            if (!src || !tgt) return null;
            return (
              <line 
                key={`e-${i}`} 
                x1={src.x} y1={src.y} 
                x2={tgt.x} y2={tgt.y} 
                stroke={src.active && tgt.active ? "#e879f9" : "#334155"} 
                strokeWidth="1" 
                opacity={src.active && tgt.active ? 0.8 : 0.3}
              />
            );
          })}
          {nodes.map(n => (
            <circle 
              key={`n-${n.id}`} 
              cx={n.x} cy={n.y} r={n.r} 
              fill={n.active ? "#d946ef" : "#475569"} 
              className="transition-all duration-300"
            />
          ))}
        </svg>
      </div>
    </div>
  );
};
