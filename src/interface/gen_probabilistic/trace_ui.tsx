import React, { useState, useEffect } from 'react';

export const ProbabilisticTrace: React.FC = () => {
  const [particles, setParticles] = useState<number[]>(Array(100).fill(1));
  const [ess, setEss] = useState(100);

  useEffect(() => {
    const interval = setInterval(() => {
      setParticles(prev => {
        let next = [...prev];
        let sumWeights = 0;
        let sumSqWeights = 0;
        
        // Simulate likelihood updates causing weight divergence
        for (let i = 0; i < 100; i++) {
           next[i] = next[i] * (0.8 + Math.random() * 0.4);
           sumWeights += next[i];
           sumSqWeights += next[i] * next[i];
        }
        
        // Calculate Effective Sample Size (ESS)
        const currentEss = (sumWeights * sumWeights) / sumSqWeights;
        setEss(currentEss);

        // Resampling step
        if (currentEss < 50) {
           next = Array(100).fill(1); // Reset uniform weights
        }
        
        return next;
      });
    }, 200);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 flex justify-between items-center border-b border-slate-700 pb-3">
        <div>
          <h2 className="text-xl font-bold text-teal-400">Gen.jl Inference</h2>
          <p className="text-xs text-slate-400">Particle Filter Resampling</p>
        </div>
      </div>

      <div className="mb-4 bg-slate-950 p-3 rounded border border-slate-800">
        <div className="text-xs text-slate-500 uppercase tracking-widest mb-1">Effective Sample Size (ESS)</div>
        <div className="flex items-center gap-3">
          <div className="h-2 flex-1 bg-slate-800 rounded overflow-hidden relative">
            <div className={`absolute top-0 bottom-0 left-0 transition-all duration-200 ${ess < 50 ? 'bg-rose-500' : 'bg-teal-500'}`} style={{width: \`\${ess}%\`}}></div>
            <div className="absolute top-0 bottom-0 left-1/2 w-0.5 bg-slate-400 z-10" title="Resampling Threshold"></div>
          </div>
          <div className="font-mono text-sm w-12 text-right">{Math.round(ess)}</div>
        </div>
      </div>

      <div className="text-[10px] text-slate-500 mb-1">Particle Weights:</div>
      <div className="flex flex-wrap gap-[1px]">
        {particles.map((w, i) => {
          // Normalize for viz
          const alpha = Math.min(1, Math.max(0.1, w / 2));
          return (
            <div key={i} className="w-2 h-2 bg-teal-400 rounded-full transition-opacity duration-200" style={{opacity: alpha}}></div>
          );
        })}
      </div>
    </div>
  );
};
