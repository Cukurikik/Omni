import React, { useState, useEffect } from 'react';

export const ContourPlot: React.FC = () => {
  const [trials, setTrials] = useState<{x: number, y: number, v: number}[]>([]);

  useEffect(() => {
    let t = 0;
    const interval = setInterval(() => {
      t++;
      
      // TPE Simulation sampling points towards minimum at (0.5, 0.5)
      const radius = Math.max(0.05, 1.0 - t * 0.05);
      const angle = t * 1.61803398875 * 2 * Math.PI; // Golden ratio sampling
      
      const px = 0.5 + Math.cos(angle) * radius * 0.5;
      const py = 0.5 + Math.sin(angle) * radius * 0.5;
      
      // Objective function value (distance from center)
      const value = Math.sqrt(Math.pow(px - 0.5, 2) + Math.pow(py - 0.5, 2));

      setTrials(prev => [...prev, { x: px, y: py, v: value }]);

      if (t >= 50) clearInterval(interval);
    }, 100);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-md mx-auto font-sans">
      <div className="mb-4 border-b border-slate-700 pb-3">
        <h2 className="text-xl font-bold text-amber-500">Optuna TPE Sampler</h2>
        <p className="text-xs text-slate-400">Hyperparameter Contour Space</p>
      </div>

      <div className="relative w-full aspect-square bg-slate-800 rounded border border-slate-600 overflow-hidden shadow-inner">
        {/* Draw contour grid deterministically */}
        <div className="absolute inset-0 grid grid-cols-10 grid-rows-10 opacity-20 pointer-events-none">
          {Array.from({length: 100}).map((_, i) => (
            <div key={i} className="border border-amber-900/30"></div>
          ))}
        </div>
        
        {/* Plot trials */}
        {trials.map((trial, i) => {
          // Color based on objective value (lower is greener/brighter)
          const heat = Math.floor((1 - trial.v * 2) * 255);
          const color = `rgb(${255 - heat}, ${heat}, 100)`;
          
          return (
            <div 
              key={i}
              className="absolute w-2 h-2 rounded-full -ml-1 -mt-1 border border-black shadow-sm transition-all"
              style={{
                left: `${trial.x * 100}%`,
                top: `${trial.y * 100}%`,
                backgroundColor: color,
                transform: `scale(${i === trials.length - 1 ? 1.5 : 1})`
              }}
            />
          );
        })}

        {/* Global Minimum Target */}
        <div className="absolute left-1/2 top-1/2 w-4 h-4 -ml-2 -mt-2 border-2 border-white rounded-full flex items-center justify-center opacity-50">
          <div className="w-1 h-1 bg-white rounded-full"></div>
        </div>
      </div>
      
      <div className="mt-4 flex justify-between text-[10px] font-mono text-slate-500">
        <div>Trials: {trials.length}</div>
        <div>Best Value: {trials.length > 0 ? Math.min(...trials.map(t=>t.v)).toFixed(4) : 'N/A'}</div>
      </div>
    </div>
  );
};
