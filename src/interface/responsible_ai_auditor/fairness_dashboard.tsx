import React, { useState, useEffect } from 'react';

export const FairnessDashboard: React.FC = () => {
  const [ratio, setRatio] = useState(0.6); // Starts failing
  const [status, setStatus] = useState("FAIL");

  useEffect(() => {
    const interval = setInterval(() => {
      setRatio(prev => {
        // Simulate model retraining mitigating bias
        const next = Math.min(0.95, prev + 0.05 + Math.random() * 0.02);
        if (next >= 0.8 && next <= 1.25) setStatus("PASS");
        return next;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 flex justify-between items-center border-b border-slate-700 pb-3">
        <div>
          <h2 className="text-xl font-bold text-violet-400">Responsible AI</h2>
          <p className="text-xs text-slate-400">Algorithmic Bias Audit</p>
        </div>
        <div className={`px-2 py-1 rounded text-xs font-bold ${status === 'PASS' ? 'bg-emerald-900/50 text-emerald-400 border border-emerald-700' : 'bg-rose-900/50 text-rose-400 border border-rose-700'}`}>
          {status}
        </div>
      </div>

      <div className="space-y-4">
        <div>
           <div className="flex justify-between text-xs font-mono mb-1">
             <span className="text-slate-400">Disparate Impact Ratio</span>
             <span className="font-bold">{ratio.toFixed(2)}</span>
           </div>
           
           <div className="relative w-full h-4 mt-2">
             {/* 80% Rule Safe Zone */}
             <div className="absolute left-[80%] right-0 top-0 bottom-0 bg-emerald-900/30 border-l border-emerald-500/50"></div>
             
             {/* Value Indicator */}
             <div className="absolute top-0 bottom-0 w-1 bg-white shadow-[0_0_8px_white] transition-all duration-300" style={{left: `${Math.min(100, ratio * 100)}%`}}></div>
             
             {/* Axis track */}
             <div className="absolute top-1/2 left-0 right-0 h-px bg-slate-700 -z-10"></div>
           </div>
           <div className="flex justify-between text-[8px] text-slate-500 mt-1">
             <span>0.0</span>
             <span>0.8 (Threshold)</span>
             <span>1.0</span>
           </div>
        </div>
      </div>
    </div>
  );
};
