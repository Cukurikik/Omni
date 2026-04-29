import React, { useEffect, useState } from 'react';

interface DagNode {
  id: string;
  throughput: number;
}

export const DataflowGraph: React.FC = () => {
  const [nodes, setNodes] = useState<DagNode[]>([]);

  useEffect(() => {
    let animationFrameId: number;
    let time = 0;

    const renderLoop = () => {
      time += 0.05;
      
      const deterministicNodes: DagNode[] = ['Extract', 'Transform_A', 'Transform_B', 'Load'].map((name, i) => {
        return {
          id: name,
          throughput: Math.abs(Math.cos(time + i)) * 1000 + 500
        };
      });

      setNodes(deterministicNodes);
      animationFrameId = requestAnimationFrame(renderLoop);
    };

    renderLoop();

    return () => cancelAnimationFrame(animationFrameId);
  }, []);

  return (
    <div className="p-6 bg-slate-800 text-green-400 font-mono rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-4">Hamilton Dataflow Lineage</h2>
      <div className="flex flex-col gap-4 relative">
        {nodes.map((node, i) => (
          <div key={node.id} className="p-4 bg-slate-900 border border-slate-700 rounded flex justify-between items-center z-10">
            <span className="font-bold">{node.id}</span>
            <span>{node.throughput.toFixed(2)} MB/s</span>
          </div>
        ))}
        {/* Draw fake connecting lines using CSS borders */}
        <div className="absolute top-10 bottom-10 left-8 border-l-2 border-green-700 z-0 opacity-50"></div>
      </div>
    </div>
  );
};
