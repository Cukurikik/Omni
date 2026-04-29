import React, { useState, useEffect } from 'react';

export const PerfDashboard: React.FC = () => {
  const [accuracy, setAccuracy] = useState(0.01);
  const [flops, setFlops] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setAccuracy(prev => {
        if (prev >= 0.759) return prev; // ResNet-50 v1.5 MLPerf target
        return Math.min(0.759, prev + (0.759 - prev) * 0.1 + Math.random() * 0.01);
      });
      setFlops(prev => prev + 120 + Math.random() * 10);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 flex justify-between items-center border-b border-slate-700 pb-3">
        <div>
          <h2 className="text-xl font-bold text-blue-500">MLPerf Training</h2>
          <p className="text-xs text-slate-400">ResNet-50 Image Classification</p>
        </div>
      </div>

      <div className="space-y-4">
        <div>
           <div className="flex justify-between text-xs font-mono mb-1">
             <span className="text-slate-400">Top-1 Accuracy</span>
             <span className={accuracy >= 0.759 ? "text-emerald-400 font-bold" : "text-blue-400 font-bold"}>
               {(accuracy * 100).toFixed(2)}% / 75.90%
             </span>
           </div>
           <div className="w-full bg-slate-800 rounded-full h-2">
             <div className="bg-blue-500 h-2 rounded-full transition-all duration-300" style={{width: `${(accuracy / 0.759) * 100}%`}}></div>
           </div>
        </div>

        <div className="bg-slate-950 p-4 rounded border border-slate-800 font-mono text-sm">
           <div className="text-slate-500 mb-1">Total Compute:</div>
           <div className="text-fuchsia-400 text-xl">{flops.toFixed(1)} PETAFLOPS</div>
        </div>
      </div>
    </div>
  );
};
