import React, { useState, useEffect } from 'react';

export const LineageGraph: React.FC = () => {
  const [nodes, setNodes] = useState<{id: string, type: string, x: number, y: number, active: boolean}[]>([]);

  useEffect(() => {
    // Deterministic static graph layout
    const initialNodes = [
      { id: 'User_DB', type: 'SOURCE', x: 50, y: 50, active: false },
      { id: 'Click_Stream', type: 'SOURCE', x: 50, y: 150, active: false },
      { id: 'Age_Calc', type: 'TRANSFORM', x: 200, y: 50, active: false },
      { id: 'Session_Agg', type: 'TRANSFORM', x: 200, y: 150, active: false },
      { id: 'User_Features', type: 'STORE', x: 350, y: 100, active: false },
      { id: 'ML_Model_v1', type: 'SINK', x: 500, y: 100, active: false },
    ];
    
    setNodes(initialNodes);

    let t = 0;
    const interval = setInterval(() => {
      t++;
      
      // Deterministic data flow animation
      setNodes(prev => prev.map(n => ({
        ...n,
        // Activate sequentially based on layout order
        active: (t % 10) === (n.x / 50) % 10 || (t % 10) === ((n.x + 50) / 50) % 10
      })));

    }, 500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-zinc-900 p-6 rounded-lg border border-zinc-700 shadow-xl max-w-2xl mx-auto font-sans">
      <div className="mb-6 border-b border-zinc-800 pb-4 flex justify-between items-end">
        <div>
          <h2 className="text-xl font-bold text-orange-400">Feature Lineage</h2>
          <p className="text-xs text-zinc-500">DAG Execution Trace</p>
        </div>
        <div className="text-xs font-mono text-zinc-400">
          MODE: REALTIME
        </div>
      </div>

      <div className="relative h-64 border border-zinc-800 rounded bg-zinc-950 overflow-hidden">
        
        {/* Static SVG Edges */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none">
          <defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
              <polygon points="0 0, 10 3.5, 0 7" fill="#52525b" />
            </marker>
            <marker id="arrowhead-active" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
              <polygon points="0 0, 10 3.5, 0 7" fill="#fb923c" />
            </marker>
          </defs>
          
          {/* Edges */}
          {[
            [50, 50, 200, 50],
            [50, 150, 200, 150],
            [200, 50, 350, 100],
            [200, 150, 350, 100],
            [350, 100, 500, 100],
          ].map(([x1, y1, x2, y2], i) => {
            // Determine if edge is active based on node states
            const sourceActive = nodes.find(n => n.x === x1 && n.y === y1)?.active;
            
            return (
              <line 
                key={i}
                x1={x1 + 30} 
                y1={y1} 
                x2={x2 - 30} 
                y2={y2} 
                stroke={sourceActive ? "#fb923c" : "#3f3f46"} 
                strokeWidth="2"
                markerEnd={`url(#${sourceActive ? 'arrowhead-active' : 'arrowhead'})`}
                className="transition-colors duration-300"
              />
            )
          })}
        </svg>

        {/* Nodes */}
        {nodes.map(node => {
          let bgColor = 'bg-zinc-800';
          let borderColor = 'border-zinc-600';
          let textColor = 'text-zinc-300';
          
          if (node.active) {
            bgColor = 'bg-orange-900/30';
            borderColor = 'border-orange-500';
            textColor = 'text-orange-300';
          }

          return (
            <div 
              key={node.id}
              className={`absolute flex flex-col items-center justify-center p-2 rounded border-2 shadow-lg transition-all duration-300 ${bgColor} ${borderColor} z-10 -translate-x-1/2 -translate-y-1/2`}
              style={{ left: `${node.x}px`, top: `${node.y}px`, width: '100px' }}
            >
              <span className={`text-[10px] font-bold ${textColor}`}>{node.id}</span>
              <span className="text-[8px] text-zinc-500 mt-1">{node.type}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
