import React, { useState, useEffect } from 'react';

export const FederatedConvergence: React.FC = () => {
  const [round, setRound] = useState(0);
  const [accuracy, setAccuracy] = useState(45.0);

  useEffect(() => {
    const interval = setInterval(() => {
      setRound(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        
        // Logarithmic accuracy curve simulation
        setAccuracy(45.0 + (Math.log(prev + 1) / Math.log(100)) * 43.5);
        return prev + 5;
      });
    }, 300);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 border-b border-slate-700 pb-2">
        <h2 className="text-xl font-bold text-blue-400">Federated Learning</h2>
        <p className="text-xs text-slate-400">Global Model Convergence</p>
      </div>

      <div className="flex gap-4 mb-4 text-center">
         <div className="flex-1 bg-slate-950 p-3 rounded border border-slate-800">
            <div className="text-2xl font-mono text-slate-300">{round}</div>
            <div className="text-[10px] uppercase text-slate-500 mt-1">Agg Rounds</div>
         </div>
         <div className="flex-1 bg-slate-950 p-3 rounded border border-blue-900/50">
            <div className="text-2xl font-mono text-blue-400">{accuracy.toFixed(1)}%</div>
            <div className="text-[10px] uppercase text-blue-500 mt-1">Accuracy</div>
         </div>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 h-[100px] relative flex items-end">
         {/* Curve rendering simulation */}
         <svg className="absolute inset-0 w-full h-full" preserveAspectRatio="none">
            <path 
              d={`M 0,100 Q 50,${100 - accuracy} 100,${100 - accuracy}`} 
              fill="none" 
              stroke="#60a5fa" 
              strokeWidth="3"
              strokeDasharray={round < 100 ? "4" : "none"}
              className={round < 100 ? "animate-pulse" : ""}
            />
         </svg>
      </div>

      <div className="mt-4 p-2 bg-slate-800 rounded text-[10px] font-mono text-slate-400 flex items-center justify-between">
         <span>Differential Privacy: <span className="text-emerald-400">Active</span></span>
         <span>Clients: 14,204</span>
      </div>
    </div>
  );
};
