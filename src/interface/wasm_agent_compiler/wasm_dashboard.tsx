import React, { useState, useEffect } from 'react';

export const WasmDashboard: React.FC = () => {
  const [compiling, setCompiling] = useState(true);
  const [size, setSize] = useState(45.2); // MB

  useEffect(() => {
    const interval = setInterval(() => {
      setSize(prev => {
        if (prev <= 3.8) {
          setCompiling(false);
          clearInterval(interval);
          return 3.8;
        }
        return prev - 4.5;
      });
    }, 300);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 border-b border-slate-700 pb-2">
        <h2 className="text-xl font-bold text-yellow-500">WASM Compiler</h2>
        <p className="text-xs text-slate-400">Agent Payload Optimization</p>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 text-center mb-4 relative overflow-hidden">
         <div className="text-[10px] uppercase font-bold text-slate-500 mb-2">Binary Size (MB)</div>
         <div className={`text-4xl font-mono transition-colors ${compiling ? 'text-rose-500' : 'text-emerald-500 font-bold'}`}>
            {size.toFixed(1)}
         </div>
         
         {compiling && (
            <div className="absolute bottom-0 left-0 h-1 bg-yellow-500 animate-pulse w-full"></div>
         )}
      </div>

      <div className="space-y-2 text-xs font-mono">
         <div className="flex justify-between items-center bg-slate-800 p-2 rounded">
            <span>Dead Code Elimination</span>
            <span className={!compiling ? "text-emerald-400" : "text-yellow-400"}>{!compiling ? 'DONE' : 'RUNNING'}</span>
         </div>
         <div className="flex justify-between items-center bg-slate-800 p-2 rounded">
            <span>Debug Symbol Stripping</span>
            <span className={size < 20 ? "text-emerald-400" : "text-slate-500"}>{size < 20 ? 'DONE' : 'WAITING'}</span>
         </div>
         <div className="flex justify-between items-center bg-slate-800 p-2 rounded">
            <span>LTO (Link-Time Opt)</span>
            <span className={size < 10 ? "text-emerald-400" : "text-slate-500"}>{size < 10 ? 'DONE' : 'WAITING'}</span>
         </div>
      </div>
    </div>
  );
};
