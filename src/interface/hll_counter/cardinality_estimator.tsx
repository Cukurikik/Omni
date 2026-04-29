import React, { useState, useEffect } from 'react';

export const CardinalityEstimator: React.FC = () => {
  const [estimate, setEstimate] = useState(0);
  const [actual, setActual] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setActual(prev => prev + Math.floor(Math.random() * 5000));
      
      // Simulate HLL error (usually within 1.04% for p=14)
      setEstimate(prev => {
        const trueVal = actual + 2500; // approximate next actual
        const errorMargin = trueVal * 0.0104; // 1.04% standard error
        const drift = (Math.random() * errorMargin * 2) - errorMargin;
        return Math.floor(trueVal + drift);
      });
    }, 800);

    return () => clearInterval(interval);
  }, [actual]);

  const diff = Math.abs(actual - estimate);
  const errorPct = actual > 0 ? ((diff / actual) * 100).toFixed(2) : '0.00';

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 flex justify-between items-center border-b border-slate-700 pb-3">
        <div>
          <h2 className="text-xl font-bold text-fuchsia-500">HyperLogLog</h2>
          <p className="text-xs text-slate-400">Cardinality Estimator</p>
        </div>
        <div className="text-[10px] font-mono bg-slate-800 text-slate-400 px-2 py-1 rounded border border-slate-700">
          p=14 (12KB)
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-slate-800 p-3 rounded border border-slate-700">
           <div className="text-[9px] text-slate-500 uppercase font-bold tracking-wider mb-1">True Count (O(N) Mem)</div>
           <div className="text-xl font-mono font-bold text-slate-300">{actual.toLocaleString()}</div>
        </div>
        <div className="bg-slate-800 p-3 rounded border border-fuchsia-900/50">
           <div className="text-[9px] text-fuchsia-500 uppercase font-bold tracking-wider mb-1">HLL Estimate (O(1) Mem)</div>
           <div className="text-xl font-mono font-bold text-fuchsia-400">{estimate.toLocaleString()}</div>
        </div>
      </div>

      <div className="bg-slate-950 p-3 rounded border border-slate-800 flex justify-between items-center">
        <div className="text-xs text-slate-400">Standard Error Rate</div>
        <div className={`font-mono text-sm font-bold ${parseFloat(errorPct) > 1.5 ? 'text-amber-500' : 'text-emerald-500'}`}>
          ± {errorPct}%
        </div>
      </div>
    </div>
  );
};
