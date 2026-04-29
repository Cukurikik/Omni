import React, { useState, useEffect } from 'react';

export const WaveformViz: React.FC = () => {
  const [waveform, setWaveform] = useState<number[]>(Array(50).fill(0));
  const [step, setStep] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setStep(s => {
        const next = s + 1;
        if (next > 100) return 100; // Diffusion complete
        
        // As diffusion steps increase, the waveform emerges from noise
        setWaveform(Array(50).fill(0).map((_, i) => {
          const noise = Math.random() * (100 - next) / 50;
          const signal = Math.sin(i * 0.5) * Math.sin(i * 0.1) * (next / 100);
          return Math.abs(signal + noise);
        }));
        
        return next;
      });
    }, 50);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-end">
        <div>
          <h2 className="text-xl font-bold text-cyan-400">Stable Audio</h2>
          <p className="text-xs text-slate-400">Latent Diffusion Synthesis</p>
        </div>
        <div className="text-xs font-mono text-cyan-500">Step: {step}/100</div>
      </div>

      <div className="h-24 bg-slate-950 p-2 rounded border border-slate-800 flex items-center justify-between gap-1 overflow-hidden">
        {waveform.map((h, i) => (
          <div 
            key={i} 
            className="w-full bg-cyan-400 rounded-sm transition-all duration-75"
            style={{ height: `${Math.max(2, h * 100)}%` }}
          />
        ))}
      </div>
      
      <div className="mt-3 text-center text-[10px] text-slate-500 font-mono uppercase tracking-widest">
        {step < 100 ? "Denoising Latent Space..." : "Audio Synthesis Complete"}
      </div>
    </div>
  );
};
