import React, { useState, useEffect } from 'react';

export const AutomatedReview: React.FC = () => {
  const [analyzing, setAnalyzing] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setAnalyzing(false);
    }, 2000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 border-b border-slate-700 pb-2">
        <h2 className="text-xl font-bold text-indigo-400">PR Review Bot</h2>
        <p className="text-xs text-slate-400">Automated Code Analysis</p>
      </div>

      <div className="bg-slate-950 p-3 rounded border border-slate-800 mb-4">
         <div className="flex justify-between items-center mb-2">
            <span className="text-xs font-mono font-bold text-white">#1024: feat(auth): add MFA</span>
            <span className="text-[10px] bg-slate-800 px-1 rounded text-slate-400">Open</span>
         </div>
         <div className="text-[10px] text-slate-500 font-mono">+142 lines, -12 lines</div>
      </div>

      <div className="bg-slate-950 rounded border border-slate-800 min-h-[140px] relative overflow-hidden flex flex-col p-3">
         
         {analyzing ? (
            <div className="flex-1 flex flex-col items-center justify-center">
               <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
               <div className="text-[10px] uppercase font-bold text-indigo-500 mt-2 tracking-widest animate-pulse">Running Checks...</div>
            </div>
         ) : (
            <div className="space-y-2 animate-fade-in">
               <div className="flex items-center gap-2 text-xs">
                  <span className="text-emerald-500">✓</span>
                  <span className="text-slate-300">Semantic Commits Validated</span>
               </div>
               <div className="flex items-center gap-2 text-xs">
                  <span className="text-emerald-500">✓</span>
                  <span className="text-slate-300">No Security Vulnerabilities</span>
               </div>
               <div className="flex items-center gap-2 text-xs">
                  <span className="text-rose-500">✖</span>
                  <span className="text-slate-300">Test Coverage Drops Below 90%</span>
               </div>
               
               <div className="mt-3 p-2 bg-rose-950/50 border border-rose-900 rounded">
                  <div className="text-[10px] font-bold text-rose-400 uppercase mb-1">Bot Action</div>
                  <div className="text-xs text-white">PR Blocked. Please add unit tests for <span className="font-mono bg-rose-900/50 px-1 rounded">mfa_service.rs</span>.</div>
               </div>
            </div>
         )}
         
      </div>
    </div>
  );
};
