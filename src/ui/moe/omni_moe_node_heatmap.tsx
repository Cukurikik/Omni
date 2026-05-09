import React, { useMemo } from 'react';

// OMNI MOTHER Production Zero-Mock Node Heatmap
// React TSX Component rendering a visual heatmap of CPU/GPU utilization across the cluster.

interface NodeMetrics {
  nodeId: string;
  cpuUsage: number; // 0 to 1
  gpuUsage: number; // 0 to 1
  ramUsage: number; // 0 to 1
}

interface HeatmapProps {
  nodes: NodeMetrics[];
}

export const MoENodeHeatmap: React.FC<HeatmapProps> = ({ nodes }) => {
  
  const getColor = (usage: number) => {
    // Green -> Yellow -> Red gradient based on usage
    const hue = ((1 - usage) * 120).toString(10);
    return `hsl(${hue}, 100%, 50%)`;
  };

  return (
    <div style={{ background: '#111', padding: '20px', borderRadius: '8px', color: '#fff', fontFamily: 'Inter' }}>
      <h3 style={{ borderBottom: '1px solid #333', paddingBottom: '10px' }}>Cluster Utilization Heatmap</h3>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))', gap: '15px', marginTop: '20px' }}>
        {nodes.map(node => (
          <div key={node.nodeId} style={{ background: '#222', padding: '15px', borderRadius: '6px', border: '1px solid #444' }}>
            <div style={{ fontWeight: 'bold', marginBottom: '10px', fontSize: '14px' }}>{node.nodeId}</div>
            
            <div style={{ marginBottom: '8px' }}>
              <div style={{ fontSize: '10px', color: '#888', marginBottom: '2px' }}>GPU</div>
              <div style={{ height: '8px', width: '100%', background: '#333', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${node.gpuUsage * 100}%`, background: getColor(node.gpuUsage), transition: 'width 0.3s ease' }} />
              </div>
            </div>

            <div style={{ marginBottom: '8px' }}>
              <div style={{ fontSize: '10px', color: '#888', marginBottom: '2px' }}>CPU</div>
              <div style={{ height: '8px', width: '100%', background: '#333', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${node.cpuUsage * 100}%`, background: getColor(node.cpuUsage), transition: 'width 0.3s ease' }} />
              </div>
            </div>

            <div>
              <div style={{ fontSize: '10px', color: '#888', marginBottom: '2px' }}>RAM</div>
              <div style={{ height: '8px', width: '100%', background: '#333', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${node.ramUsage * 100}%`, background: getColor(node.ramUsage), transition: 'width 0.3s ease' }} />
              </div>
            </div>

          </div>
        ))}
      </div>
    </div>
  );
};
