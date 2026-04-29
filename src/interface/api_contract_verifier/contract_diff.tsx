import React, { useState, useEffect } from 'react';

export const ContractDiff: React.FC = () => {
  const [fuzzing, setFuzzing] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setFuzzing(false);
    }, 2500);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 border-b border-slate-700 pb-2 flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-orange-400">API Contract</h2>
          <p className="text-xs text-slate-400">OpenAPI Diff Verifier</p>
        </div>
        {fuzzing && <div className="w-4 h-4 border-2 border-orange-500 border-t-transparent rounded-full animate-spin"></div>}
      </div>

      <div className="bg-slate-950 rounded border border-slate-800 text-xs font-mono overflow-hidden mb-4">
         <div className="bg-slate-900 px-3 py-1 border-b border-slate-800 flex gap-2">
            <span className="text-emerald-400 font-bold">GET</span>
            <span className="text-slate-300">/api/v2/users/profile</span>
         </div>
         <div className="p-3 space-y-1">
            <div className="text-slate-500">Response Schema:</div>
            <div className="ml-2 text-slate-300">"id": <span className="text-sky-400">UUID</span></div>
            <div className="ml-2 text-slate-300">"username": <span className="text-sky-400">String</span></div>
            <div className="ml-2 bg-rose-900/30 text-rose-300 px-1 -mx-1 flex justify-between">
               <span>- "email": <span className="text-sky-400">String</span></span>
               <span className="bg-rose-900 text-rose-200 px-1 rounded text-[8px] uppercase">Removed</span>
            </div>
            <div className="ml-2 bg-emerald-900/30 text-emerald-300 px-1 -mx-1 flex justify-between">
               <span>+ "emails": <span className="text-sky-400">Array&lt;String&gt;</span></span>
               <span className="bg-emerald-900 text-emerald-200 px-1 rounded text-[8px] uppercase">Added</span>
            </div>
         </div>
      </div>

      {!fuzzing && (
         <div className="bg-rose-950/50 p-3 rounded border border-rose-900 shadow-[0_0_15px_rgba(225,29,72,0.2)] animate-fade-in">
            <div className="text-[10px] uppercase font-bold text-rose-500 mb-1 flex items-center gap-1">
               <span className="text-sm">⚠️</span> Breaking Change Detected
            </div>
            <p className="text-xs text-rose-200">
               Field <span className="font-mono bg-rose-900 px-1 rounded">email</span> was removed. This violates Semantic Versioning policies for v2 APIs.
            </p>
         </div>
      )}
    </div>
  );
};
