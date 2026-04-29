import React, { useEffect, useRef } from 'react';

export const UMAPVisualizer: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let time = 0;

    const render = () => {
      time += 0.01;
      ctx.fillStyle = '#000000';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      const numPoints = 200;
      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;

      for (let i = 0; i < numPoints; i++) {
        // Deterministic clustering math
        const cluster = i % 3;
        const angle = (i * 137.5) + time * (cluster === 0 ? 1 : (cluster === 1 ? -0.5 : 0.8));
        const radius = (i % 50) * 2 + 20;

        let clusterOffsetX = 0;
        let clusterOffsetY = 0;
        let color = '#fff';

        if (cluster === 0) {
          clusterOffsetX = -50; clusterOffsetY = -50; color = '#3b82f6'; // blue
        } else if (cluster === 1) {
          clusterOffsetX = 60; clusterOffsetY = -30; color = '#10b981'; // green
        } else {
          clusterOffsetX = 0; clusterOffsetY = 60; color = '#ec4899'; // pink
        }

        const x = centerX + clusterOffsetX + Math.cos(angle) * radius;
        const y = centerY + clusterOffsetY + Math.sin(angle) * radius;

        ctx.beginPath();
        ctx.arc(x, y, 2, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => cancelAnimationFrame(animationFrameId);
  }, []);

  return (
    <div className="w-full flex flex-col items-center justify-center p-8 bg-black rounded-lg">
      <h2 className="text-xl text-white font-mono mb-4">Scanpy UMAP Projection</h2>
      <canvas ref={canvasRef} width={400} height={400} className="rounded border border-gray-800" />
    </div>
  );
};
