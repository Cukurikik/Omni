import React, { useEffect, useRef } from 'react';

export const CausalGraphUI: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let time = 0;

    const render = () => {
      time += 0.02;
      ctx.fillStyle = '#f8fafc'; // slate-50
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      const nodes = [
        { x: 100, y: 100, label: 'Age' },
        { x: 100, y: 300, label: 'Diet' },
        { x: 300, y: 200, label: 'Blood Pressure' },
        { x: 500, y: 200, label: 'Heart Disease' }
      ];

      const edges = [
        { from: 0, to: 2 },
        { from: 1, to: 2 },
        { from: 2, to: 3 },
        { from: 0, to: 3 }
      ];

      // Draw Edges
      edges.forEach((edge, i) => {
        const p1 = nodes[edge.from];
        const p2 = nodes[edge.to];
        const causalStrength = Math.abs(Math.sin(time + i)) * 3 + 1;
        
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.strokeStyle = `rgba(59, 130, 246, ${causalStrength / 4})`; // blue-500
        ctx.lineWidth = causalStrength;
        ctx.stroke();
      });

      // Draw Nodes
      nodes.forEach(node => {
        ctx.beginPath();
        ctx.arc(node.x, node.y, 30, 0, Math.PI * 2);
        ctx.fillStyle = '#ffffff';
        ctx.fill();
        ctx.strokeStyle = '#94a3b8'; // slate-400
        ctx.lineWidth = 2;
        ctx.stroke();

        ctx.fillStyle = '#0f172a';
        ctx.font = '12px monospace';
        ctx.textAlign = 'center';
        ctx.fillText(node.label, node.x, node.y + 4);
      });

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => cancelAnimationFrame(animationFrameId);
  }, []);

  return (
    <div className="w-full flex flex-col items-center justify-center p-8 bg-white border border-gray-200 rounded-lg shadow-sm">
      <h2 className="text-xl text-gray-800 font-mono mb-4">CausalNex Graph Intervention Planner</h2>
      <canvas ref={canvasRef} width={600} height={400} className="rounded" />
    </div>
  );
};
