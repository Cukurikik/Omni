import React, { useEffect, useRef, useState } from 'react';

interface Point {
  x: number;
  y: number;
  word: string;
}

export const ScatterPlot: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [points, setPoints] = useState<Point[]>([]);

  useEffect(() => {
    // Deterministic pseudo-data generation
    const words = ["algorithm", "data", "model", "neural", "tensor", "matrix", "vector", "layer"];
    const generated: Point[] = words.map((w, i) => ({
      x: ((i * 37) % 100) / 100, // pseudo-random deterministic
      y: ((i * 59) % 100) / 100,
      word: w
    }));
    setPoints(generated);
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || points.length === 0) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Axes
    ctx.strokeStyle = '#e5e7eb';
    ctx.beginPath();
    ctx.moveTo(50, 50); ctx.lineTo(50, 350); // Y
    ctx.moveTo(50, 350); ctx.lineTo(350, 350); // X
    ctx.stroke();

    // Plot
    points.forEach(p => {
      const px = 50 + p.x * 300;
      const py = 350 - p.y * 300;
      
      ctx.fillStyle = '#3b82f6';
      ctx.beginPath();
      ctx.arc(px, py, 4, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = '#4b5563';
      ctx.font = '12px sans-serif';
      ctx.fillText(p.word, px + 8, py + 4);
    });
  }, [points]);

  return (
    <div className="p-6 bg-white rounded-xl shadow border border-gray-100 flex flex-col items-center">
      <h3 className="text-xl font-bold text-gray-800 mb-4">Scattertext Visualization</h3>
      <canvas ref={canvasRef} width={400} height={400} className="border border-gray-200 rounded" />
    </div>
  );
};
