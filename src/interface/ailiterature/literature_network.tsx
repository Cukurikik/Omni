import React, { useEffect, useRef, useState } from 'react';

// OMNI INTERFACE LAYER: AI Literature Network
// WebGL/Canvas rendered force-directed graph of AI papers.

interface PaperNode {
  id: string;
  x: number;
  y: number;
  title: string;
  pagerank: number;
}

interface PaperEdge {
  source: string;
  target: string;
}

export const LiteratureNetwork: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [nodes, setNodes] = useState<PaperNode[]>([]);
  const [edges, setEdges] = useState<PaperEdge[]>([]);

  useEffect(() => {
    // Fetch pre-computed layout from C++ FFI via Bridge
    const loadGraph = async () => {
      try {
        const res = await fetch('/api/omni/literature/graph');
        const json = await res.json();
        if (json.status === 'Ok') {
          setNodes(json.payload.nodes);
          setEdges(json.payload.edges);
        }
      } catch (err) {
        console.error("OmniBridge Error:", err);
      }
    };
    loadGraph();
  }, []);

  useEffect(() => {
    if (!canvasRef.current || nodes.length === 0) return;
    const ctx = canvasRef.current.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, 1000, 800);

    // Draw Edges
    ctx.strokeStyle = 'rgba(100, 149, 237, 0.2)';
    ctx.lineWidth = 1;
    edges.forEach(edge => {
      const source = nodes.find(n => n.id === edge.source);
      const target = nodes.find(n => n.id === edge.target);
      if (source && target) {
        ctx.beginPath();
        ctx.moveTo(source.x, source.y);
        ctx.lineTo(target.x, target.y);
        ctx.stroke();
      }
    });

    // Draw Nodes
    nodes.forEach(node => {
      const radius = Math.max(3, node.pagerank * 50);
      ctx.fillStyle = '#ffcc00';
      ctx.beginPath();
      ctx.arc(node.x, node.y, radius, 0, Math.PI * 2);
      ctx.fill();

      // Draw title for highly ranked nodes
      if (node.pagerank > 0.05) {
        ctx.fillStyle = '#ffffff';
        ctx.font = '10px Arial';
        ctx.fillText(node.title, node.x + radius + 5, node.y + 3);
      }
    });
  }, [nodes, edges]);

  return (
    <div className="bg-[#0f172a] p-6 text-white min-h-screen">
      <h1 className="text-3xl font-serif text-blue-300 mb-4">OMNI AI Citation Network</h1>
      <p className="text-gray-400 mb-6 font-mono text-sm">Force-directed topological mapping of the latest AI breakthroughs.</p>
      
      <div className="border border-blue-900 rounded-lg overflow-hidden bg-black shadow-2xl relative">
        <canvas ref={canvasRef} width={1000} height={800} className="w-full h-auto cursor-grab active:cursor-grabbing" />
        
        {nodes.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <span className="animate-pulse text-blue-500 font-mono">Running C++ Fruchterman-Reingold Kernel...</span>
          </div>
        )}
      </div>
    </div>
  );
};
