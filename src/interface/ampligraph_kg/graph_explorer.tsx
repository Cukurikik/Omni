import React, { useState } from 'react';

interface Node {
  id: string;
  x: number;
  y: number;
  label: string;
}

interface Edge {
  source: string;
  target: string;
  label: string;
}

export const GraphExplorer: React.FC = () => {
  const [nodes] = useState<Node[]>([
    { id: '1', x: 150, y: 150, label: 'OmniEngine' },
    { id: '2', x: 350, y: 100, label: 'Rust' },
    { id: '3', x: 350, y: 200, label: 'TypeScript' }
  ]);
  
  const [edges] = useState<Edge[]>([
    { source: '1', target: '2', label: 'written_in' },
    { source: '1', target: '3', label: 'interface_in' }
  ]);

  return (
    <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200 w-full max-w-2xl font-sans text-gray-800">
      <h2 className="text-xl font-bold mb-4">Knowledge Graph Explorer</h2>
      
      <div className="relative h-64 w-full bg-gray-50 border border-gray-200 rounded overflow-hidden shadow-inner">
        <svg className="w-full h-full absolute top-0 left-0">
          {/* Draw edges */}
          {edges.map((edge, i) => {
            const sourceNode = nodes.find(n => n.id === edge.source);
            const targetNode = nodes.find(n => n.id === edge.target);
            if (!sourceNode || !targetNode) return null;
            
            const midX = (sourceNode.x + targetNode.x) / 2;
            const midY = (sourceNode.y + targetNode.y) / 2;

            return (
              <g key={`edge-${i}`}>
                <line 
                  x1={sourceNode.x} y1={sourceNode.y} 
                  x2={targetNode.x} y2={targetNode.y} 
                  stroke="#94a3b8" strokeWidth="2" 
                />
                <text x={midX} y={midY - 5} fontSize="10" fill="#64748b" textAnchor="middle" className="bg-white px-1">
                  {edge.label}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Draw nodes */}
        {nodes.map(node => (
          <div 
            key={node.id}
            className="absolute transform -translate-x-1/2 -translate-y-1/2 flex flex-col items-center group cursor-pointer"
            style={{ left: node.x, top: node.y }}
          >
            <div className="w-12 h-12 bg-indigo-600 rounded-full shadow-md flex items-center justify-center text-white font-bold group-hover:scale-110 transition-transform">
              {node.id}
            </div>
            <div className="mt-1 text-xs font-semibold text-gray-700 bg-white/80 px-2 py-0.5 rounded shadow-sm border border-gray-200">
              {node.label}
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 p-3 bg-indigo-50 text-indigo-800 rounded border border-indigo-100 text-sm">
        <span className="font-semibold">TransE Embedding Context:</span> Graph visualization rendering correctly.
      </div>
    </div>
  );
};
