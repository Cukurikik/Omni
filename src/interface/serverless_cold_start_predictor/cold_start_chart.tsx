import React, { useState, useEffect } from 'react';

export const ColdStartChart: React.FC = () => {
  const [prob, setProb] = useState(0.1);
  const [warm, setWarm] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate Poisson arrival probability rising as time passes without an event
      setProb(p => {
         const next = p + 0.15;
         if (next >= 0.8) {
            setWarm(true);
            setTimeout(() => {
               setProb(0.1); // Event happened, reset probability
               setWarm(false);
            }, 1000);
         }
         return next;
      });
    }, 400);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-yellow-400">Cold-Start ML</h2>
          <p className="text-xs text-slate-400">Poisson Pre-Warming</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-bold uppercase border ${warm ? 'bg-orange-900/50 text-orange-400 border-orange-800' : 'bg-slate-800 text-slate-400 border-slate-600'}`}>
           {warm ? 'VM Booted (5ms)' : 'Idling (0W)'}
        </div>
      </div>

      <div className="bg-slate-950 p-6 rounded border border-slate-800 flex flex-col items-center justify-center mb-4">
         <div className="text-[10px] uppercase font-bold text-slate-500 mb-2">Invocation Probability</div>
         <div className="text-5xl font-mono text-yellow-400 mb-2">
            {(prob * 100).toFixed(0)}%
         </div>
         
         {/* Probability Bar */}
         <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden mt-2 relative">
            <div className="absolute inset-0 bg-yellow-500 transition-all duration-300" style={{ width: `${Math.min(100, prob * 100)}%` }}></div>
            {/* Pre-warm Threshold Line */}
            <div className="absolute top-0 bottom-0 w-0.5 bg-rose-500 z-10" style={{ left: '80%' }}></div>
         </div>
         <div className="w-full flex justify-between text-[8px] text-slate-500 font-mono mt-1">
            <span>0%</span>
            <span className="text-rose-500">80% Threshold</span>
            <span>100%</span>
         </div>
      </div>
      
      <div className="text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded border border-slate-700 text-center">
         Firecracker microVM snapshot restore: <span className="text-emerald-400 font-bold">READY</span>
      </div>
    </div>
  );
};
