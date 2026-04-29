import React, { useState, useEffect } from 'react';

export const PosteriorPlot: React.FC = () => {
  const [points, setPoints] = useState<{x: number, y: number, var: number}[]>([]);

  useEffect(() => {
    // Deterministic simulation of a GP Posterior Gaussian Distribution
    let t = 0;
    const interval = setInterval(() => {
      t++;
      
      const newPoints = Array.from({length: 40}, (_, i) => {
        const x = i;
        // True function sine wave, GP tries to fit it
        const trueY = Math.sin(x * 0.2 + t * 0.05) * 50 + 100;
        
        // Variance depends on distance from training points deterministically
        // Let's pretend training points are at x=10, 20, 30
        const dist1 = Math.abs(x - 10);
        const dist2 = Math.abs(x - 20);
        const dist3 = Math.abs(x - 30);
        const minDist = Math.min(dist1, dist2, dist3);
        
        const variance = Math.min(30, minDist * 2);
        
        return { x, y: trueY, var: variance };
      });
      
      setPoints(newPoints);
    }, 100);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-2xl mx-auto font-sans">
      <div className="mb-6 border-b border-slate-800 pb-4">
        <h2 className="text-xl font-bold text-teal-400">GPFlow Posterior</h2>
        <p className="text-xs text-slate-500">Gaussian Process RBF Kernel</p>
      </div>

      <div className="relative h-64 bg-slate-950 border border-slate-800 overflow-hidden">
        
        <svg className="absolute inset-0 w-full h-full" viewBox="0 0 40 200" preserveAspectRatio="none">
          {/* Uncertainty Band (Confidence Interval) */}
          <polygon 
            points={
              points.map(p => `${p.x},${p.y - p.var}`).join(' ') + ' ' + 
              [...points].reverse().map(p => `${p.x},${p.y + p.var}`).join(' ')
            }
            fill="rgba(20, 184, 166, 0.15)" // teal-500 low opacity
          />
          
          {/* Mean Prediction Line */}
          <polyline 
            points={points.map(p => `${p.x},${p.y}`).join(' ')}
            fill="none"
            stroke="#14b8a6" // teal-500
            strokeWidth="0.5"
          />

          {/* Training Points Markers */}
          <circle cx="10" cy={points[10]?.y || 100} r="1" fill="#fde047" />
          <circle cx="20" cy={points[20]?.y || 100} r="1" fill="#fde047" />
          <circle cx="30" cy={points[30]?.y || 100} r="1" fill="#fde047" />
        </svg>

      </div>

      <div className="mt-4 flex justify-between text-xs text-slate-500">
        <span className="flex items-center gap-2"><div className="w-2 h-2 bg-teal-500/30 rounded"></div> 95% Confidence</span>
        <span className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-yellow-300"></div> Evidence</span>
      </div>
    </div>
  );
};
