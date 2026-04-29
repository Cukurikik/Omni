import React, { useEffect, useRef } from 'react';

export const ClusterView: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let time = 0;

    const render = () => {
      time += 0.05;
      ctx.fillStyle = '#0f172a'; // slate-900
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      const numPods = 25;
      const radius = 100;
      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;

      for (let i = 0; i < numPods; i++) {
        const angle = (i / numPods) * Math.PI * 2 + time * 0.2;
        
        // Deterministic resource load mapped to size
        const load = Math.abs(Math.sin(time + i * 0.5));
        const podSize = 5 + load * 10;
        
        const x = centerX + Math.cos(angle) * radius;
        const y = centerY + Math.sin(angle) * radius;

        ctx.beginPath();
        ctx.arc(x, y, podSize, 0, Math.PI * 2);
        ctx.fillStyle = load > 0.8 ? '#ef4444' : '#22c55e';
        ctx.fill();
        
        // Draw connection to center (Ray Head Node)
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.lineTo(x, y);
        ctx.strokeStyle = `rgba(148, 163, 184, ${0.2 + load * 0.3})`;
        ctx.stroke();
      }

      // Head Node
      ctx.beginPath();
      ctx.arc(centerX, centerY, 15, 0, Math.PI * 2);
      ctx.fillStyle = '#3b82f6';
      ctx.fill();

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => cancelAnimationFrame(animationFrameId);
  }, []);

  return (
    <div className="w-full flex flex-col items-center justify-center p-8 bg-slate-900 rounded-lg">
      <h2 className="text-xl text-white font-mono mb-4">KubeRay Cluster Topology</h2>
      <canvas ref={canvasRef} width={400} height={400} className="rounded border border-slate-700 shadow-2xl" />
    </div>
  );
};
