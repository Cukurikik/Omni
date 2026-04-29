import React, { useEffect, useRef } from 'react';

export const LabNotebook: React.FC = () => {
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
      
      // Clear with dark theme
      ctx.fillStyle = '#1e1e1e';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Draw mathematical function visualization (e.g. Sine wave with decaying amplitude)
      ctx.beginPath();
      ctx.moveTo(0, canvas.height / 2);
      
      for (let x = 0; x < canvas.width; x++) {
        const normalizedX = x / 50;
        // Function: e^(-0.1x) * sin(x + t)
        const y = Math.exp(-0.1 * normalizedX) * Math.sin(normalizedX * 2 + time) * 100;
        ctx.lineTo(x, canvas.height / 2 - y);
      }
      
      ctx.strokeStyle = '#00ffff';
      ctx.lineWidth = 2;
      ctx.stroke();

      // Axis lines
      ctx.strokeStyle = '#555';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(0, canvas.height / 2);
      ctx.lineTo(canvas.width, canvas.height / 2);
      ctx.stroke();

      // HUD
      ctx.fillStyle = '#fff';
      ctx.font = '14px Consolas';
      ctx.fillText('f(x) = e^(-0.1x) * sin(2x + t)', 20, 30);
      
      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => cancelAnimationFrame(animationFrameId);
  }, []);

  return (
    <div className="w-full flex flex-col p-6 bg-[#252526] rounded border border-[#3e3e42]">
      <h2 className="text-xl text-blue-400 font-mono mb-4">Hedgehog Lab: Scientific WebGL Output</h2>
      <canvas ref={canvasRef} width={600} height={300} className="rounded shadow-inner bg-[#1e1e1e] mx-auto block" />
    </div>
  );
};
