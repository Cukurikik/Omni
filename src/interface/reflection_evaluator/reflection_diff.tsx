import React, { useState, useEffect } from 'react';

export const ReflectionDiff: React.FC = () => {
  const [reflectionState, setReflectionState] = useState(0); // 0: draft, 1: critiquing, 2: refined

  useEffect(() => {
    const timer1 = setTimeout(() => setReflectionState(1), 1500);
    const timer2 = setTimeout(() => setReflectionState(2), 3500);
    return () => { clearTimeout(timer1); clearTimeout(timer2); };
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-rose-400">Reflection Engine</h2>
        <p className="text-xs text-slate-400">LLM Self-Critique & Refinement</p>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 text-xs font-mono mb-4 relative">
         <div className="text-[10px] uppercase text-slate-500 mb-2 border-b border-slate-800 pb-1">Draft v1</div>
         <p className={`text-slate-300 transition-opacity ${reflectionState === 2 ? 'line-through opacity-50' : ''}`}>
           The server architecture uses a REST API to communicate with the database directly.
         </p>
         
         {reflectionState >= 1 && (
           <div className={`absolute right-2 top-2 px-2 py-1 bg-amber-900/50 text-amber-400 border border-amber-700/50 rounded text-[8px] animate-pulse ${reflectionState === 2 ? 'hidden' : ''}`}>
             Generating Critique...
           </div>
         )}
      </div>

      {reflectionState === 2 && (
        <div className="bg-slate-950 p-4 rounded border border-emerald-900/50 text-xs font-mono animate-fade-in relative shadow-[0_0_15px_rgba(16,185,129,0.1)]">
           <div className="text-[10px] uppercase text-emerald-500 mb-2 border-b border-emerald-900/50 pb-1 flex justify-between">
              <span>Refined v2</span>
              <span>+12.5% Confidence</span>
           </div>
           <p className="text-emerald-300">
             The server architecture uses a REST API to communicate with a <span className="bg-emerald-900/50 font-bold px-1 rounded">middleware service</span>, which then securely handles database transactions.
           </p>
        </div>
      )}
    </div>
  );
};
