// moe_expert_graph.tsx — Interface / Analytics
// Layer: UI / Visualization — MoE Token Routing Graph
//
// React component that uses D3/Canvas concepts (abstracted) to visualize
// the bipartite graph of tokens routing to experts in real-time.

import React, { useMemo } from 'react';

export interface RouteEdge {
  tokenId: number;
  expertId: number;
  weight: number; // 0.0 to 1.0
}

interface Props {
  numTokens: number;
  numExperts: number;
  routes: RouteEdge[];
}

export const MoERoutingGraph: React.FC<Props> = ({ numTokens, numExperts, routes }) => {
  // SVG Dimensions
  const width = 800;
  const height = 400;
  const padding = 40;

  // Calculate node positions
  const tokenNodes = useMemo(() => {
    return Array.from({ length: numTokens }).map((_, i) => ({
      id: i,
      x: padding,
      y: padding + (i * (height - 2 * padding)) / Math.max(1, numTokens - 1)
    }));
  }, [numTokens, height]);

  const expertNodes = useMemo(() => {
    return Array.from({ length: numExperts }).map((_, i) => ({
      id: i,
      x: width - padding,
      y: padding + (i * (height - 2 * padding)) / Math.max(1, numExperts - 1)
    }));
  }, [numExperts, height]);

  return (
    <div className="bg-gray-900 rounded-lg p-4 font-sans shadow-lg overflow-hidden">
      <h3 className="text-white font-bold mb-2">Token-to-Expert Routing Bipartite Graph</h3>
      <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`}>
        {/* Draw Edges */}
        {routes.map((edge, idx) => {
          const tNode = tokenNodes[edge.tokenId];
          const eNode = expertNodes[edge.expertId];
          
          if (!tNode || !eNode) return null;

          // Bezier curve for smooth connection
          const controlPointX1 = tNode.x + (eNode.x - tNode.x) / 3;
          const controlPointX2 = tNode.x + 2 * (eNode.x - tNode.x) / 3;
          
          const path = `M ${tNode.x} ${tNode.y} C ${controlPointX1} ${tNode.y}, ${controlPointX2} ${eNode.y}, ${eNode.x} ${eNode.y}`;
          
          return (
            <path
              key={`edge-${idx}`}
              d={path}
              fill="none"
              stroke={`rgba(59, 130, 246, ${edge.weight})`} // Blue with opacity based on routing weight
              strokeWidth={Math.max(1, edge.weight * 3)}
              className="transition-all duration-300"
            />
          );
        })}

        {/* Draw Token Nodes */}
        {tokenNodes.map(node => (
          <g key={`token-${node.id}`}>
            <circle cx={node.x} cy={node.y} r={4} fill="#10B981" />
            <text x={node.x - 10} y={node.y + 4} fill="#9CA3AF" fontSize="10" textAnchor="end">
              T{node.id}
            </text>
          </g>
        ))}

        {/* Draw Expert Nodes */}
        {expertNodes.map(node => (
          <g key={`expert-${node.id}`}>
            <circle cx={node.x} cy={node.y} r={6} fill="#F59E0B" />
            <text x={node.x + 12} y={node.y + 4} fill="#9CA3AF" fontSize="10" textAnchor="start">
              Expert {node.id}
            </text>
          </g>
        ))}
      </svg>
      
      <div className="flex justify-between mt-2 text-xs text-gray-400">
        <span>Input Tokens (N={numTokens})</span>
        <span>MoE Layers (E={numExperts})</span>
      </div>
    </div>
  );
};
