import React, { useEffect, useRef, useState } from 'react';

export const WaveformEditor: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [pitch, setPitch] = useState(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const render = () => {
      ctx.fillStyle = '#1e1e1e';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.beginPath();
      ctx.moveTo(0, canvas.height / 2);

      // Deterministic waveform rendering based on pitch
      const freqMultiplier = Math.pow(2, pitch / 12);
      
      for (let x = 0; x < canvas.width; x++) {
        const t = x / 50;
        const y = Math.sin(t * freqMultiplier * 2) * 50 + Math.sin(t * freqMultiplier * 5) * 20;
        ctx.lineTo(x, canvas.height / 2 - y);
      }

      ctx.strokeStyle = '#00ff88';
      ctx.lineWidth = 2;
      ctx.stroke();
    };

    render();
  }, [pitch]);

  return (
    <div className="p-6 bg-gray-900 text-white rounded-lg shadow-xl w-full max-w-2xl mx-auto font-mono">
      <h2 className="text-xl text-green-400 mb-4 border-b border-green-900 pb-2">Omni DSP: Audiomentations</h2>
      
      <canvas ref={canvasRef} width={600} height={200} className="w-full bg-black rounded border border-gray-700 mb-6" />

      <div className="flex items-center space-x-4">
        <label className="text-sm text-gray-400 w-32">Pitch (Semitones):</label>
        <input 
          type="range" 
          min="-12" 
          max="12" 
          step="0.5" 
          value={pitch}
          onChange={(e) => setPitch(parseFloat(e.target.value))}
          className="flex-1 accent-green-500"
        />
        <span className="w-12 text-right font-bold text-green-400">{pitch > 0 ? '+' : ''}{pitch}</span>
      </div>
    </div>
  );
};
