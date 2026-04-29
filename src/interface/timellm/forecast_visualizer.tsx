import React, { useState, useEffect, useRef } from 'react';

export const ForecastVisualizer: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [mse, setMse] = useState<number>(0.0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let frame = 0;
    const width = canvas.width;
    const height = canvas.height;

    const renderLoop = () => {
      frame += 0.02;
      ctx.fillStyle = '#0f172a'; // slate-900
      ctx.fillRect(0, 0, width, height);

      // Render historical data (white)
      ctx.beginPath();
      ctx.strokeStyle = '#e2e8f0'; // slate-200
      ctx.lineWidth = 2;
      for(let x = 0; x < width * 0.7; x += 5) {
        const y = height/2 + Math.sin(x * 0.02 + frame) * 40 + Math.cos(x * 0.05) * 20;
        if(x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();

      // Render forecast (purple)
      ctx.beginPath();
      ctx.strokeStyle = '#a855f7'; // purple-500
      ctx.lineWidth = 3;
      ctx.setLineDash([5, 5]);
      for(let x = width * 0.7; x < width; x += 5) {
        // Forecast math function
        const y = height/2 + Math.sin(x * 0.02 + frame) * 40 + Math.cos(x * 0.05) * 20;
        if(x === width * 0.7) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();
      ctx.setLineDash([]); // reset

      // Update MSE display
      setMse(Number((0.02 + Math.sin(frame * 0.5) * 0.005).toFixed(4)));

      requestAnimationFrame(renderLoop);
    };

    const id = requestAnimationFrame(renderLoop);
    return () => cancelAnimationFrame(id);
  }, []);

  return (
    <div className="bg-slate-950 p-8 rounded-lg shadow-2xl font-mono text-slate-300">
      <h2 className="text-2xl font-bold text-purple-400 mb-6">Time-LLM Generative Forecast</h2>
      
      <div className="mb-4 flex gap-8">
        <div className="bg-slate-900 p-4 rounded border border-slate-800">
          <div className="text-sm text-slate-500">Reprogramming Metric (MSE)</div>
          <div className="text-xl font-bold text-emerald-400">{mse}</div>
        </div>
        <div className="bg-slate-900 p-4 rounded border border-slate-800">
          <div className="text-sm text-slate-500">LLM Context Window</div>
          <div className="text-xl font-bold text-blue-400">4096 tokens</div>
        </div>
      </div>

      <div className="border border-slate-800 rounded bg-slate-900 overflow-hidden relative">
        <div className="absolute top-4 left-4 flex gap-4 text-xs">
          <span className="flex items-center gap-2"><span className="w-3 h-3 bg-slate-200 rounded-full"></span> History</span>
          <span className="flex items-center gap-2"><span className="w-3 h-3 bg-purple-500 rounded-full"></span> LLM Prediction</span>
        </div>
        <canvas ref={canvasRef} width={800} height={300} className="w-full" />
      </div>
    </div>
  );
};
