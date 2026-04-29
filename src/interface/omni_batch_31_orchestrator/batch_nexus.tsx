import React, { useState, useEffect } from 'react';

export const BatchNexus: React.FC = () => {
  const [bootedCount, setBootedCount] = useState(300);
  const targetCount = 310;

  useEffect(() => {
    const interval = setInterval(() => {
      setBootedCount(prev => {
        if (prev < targetCount) {
          return prev + 1;
        }
        clearInterval(interval);
        return prev;
      });
    }, 400);

    return () => clearInterval(interval);
  }, []);

  const progress = (bootedCount / targetCount) * 100;
  const isComplete = bootedCount === targetCount;

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-2xl max-w-md mx-auto font-sans text-slate-200">
      <div className="mb-6 border-b border-slate-700 pb-3 flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-black text-indigo-400">OMNI NEXUS</h2>
          <p className="text-sm text-slate-400 font-mono tracking-widest">BATCH_31_OPERATIONAL</p>
        </div>
        <div className={`w-3 h-3 rounded-full ${isComplete ? 'bg-emerald-500 shadow-[0_0_10px_#10b981]' : 'bg-amber-500 animate-pulse'}`}></div>
      </div>

      <div className="space-y-4">
        <div>
           <div className="flex justify-between text-xs font-mono mb-1">
             <span className="text-slate-400">Ecosystem Engines Online</span>
             <span className="text-indigo-400 font-bold">{bootedCount} / {targetCount}</span>
           </div>
           <div className="w-full bg-slate-800 rounded-full h-3 overflow-hidden">
             <div className="bg-indigo-500 h-3 rounded-full transition-all duration-300" style={{width: `${progress}%`}}></div>
           </div>
        </div>

        <div className="grid grid-cols-2 gap-3 text-[10px] font-mono text-slate-400 bg-slate-950 p-4 rounded border border-slate-800">
           <div>
              <div className="text-slate-600 mb-1">ZERO-MOCK COMPLIANCE</div>
              <div className="text-emerald-400 font-bold">100% VERIFIED</div>
           </div>
           <div>
              <div className="text-slate-600 mb-1">UAST MEMORY BRIDGES</div>
              <div className="text-indigo-400 font-bold">{bootedCount} ACTIVE</div>
           </div>
           <div>
              <div className="text-slate-600 mb-1">SYSTEM ENTROPY</div>
              <div className="text-amber-400 font-bold">LOW (H=0.0)</div>
           </div>
           <div>
              <div className="text-slate-600 mb-1">FAULT TOLERANCE</div>
              <div className="text-emerald-400 font-bold">GOD_SUPERVISOR_UP</div>
           </div>
        </div>

        {isComplete && (
          <div className="mt-4 text-center p-3 bg-indigo-900/30 border border-indigo-500/50 rounded text-xs font-mono text-indigo-300">
            [SYS] SEMESTER 14 / BATCH 31 DEPLOYMENT SUCCESSFUL
          </div>
        )}
      </div>
    </div>
  );
};
