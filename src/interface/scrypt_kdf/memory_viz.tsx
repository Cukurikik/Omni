import React, { useState, useEffect } from 'react';

export const MemoryViz: React.FC = () => {
  const [params, setParams] = useState({ N: 16384, r: 8, p: 1 });
  const [memoryMb, setMemoryMb] = useState(0);

  useEffect(() => {
    // Memory = 128 * r * N bytes
    const bytes = 128 * params.r * params.N;
    setMemoryMb(bytes / (1024 * 1024));
  }, [params]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 border-b border-slate-700 pb-2">
        <h2 className="text-xl font-bold text-indigo-400">Scrypt KDF</h2>
        <p className="text-xs text-slate-400">SMix Memory Hardness Configuration</p>
      </div>

      <div className="flex flex-col gap-4">
        <div className="bg-slate-800 p-4 rounded border border-slate-700">
          <div className="flex justify-between items-center mb-2">
            <span className="text-xs font-bold text-slate-400 uppercase">Cost Factor (N)</span>
            <span className="text-sm font-mono font-bold text-indigo-400">{params.N}</span>
          </div>
          <input 
            type="range" 
            min="10" max="18" 
            value={Math.log2(params.N)}
            onChange={(e) => setParams({...params, N: Math.pow(2, parseInt(e.target.value))})}
            className="w-full accent-indigo-500 h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer"
          />
        </div>

        <div className="bg-slate-800 p-4 rounded border border-slate-700">
           <div className="flex justify-between items-center mb-1">
             <span className="text-xs font-bold text-slate-400 uppercase">Memory Required</span>
           </div>
           <div className="text-3xl font-black font-mono text-emerald-400">
             {memoryMb.toFixed(2)} <span className="text-lg">MB</span>
           </div>
           <div className="text-[10px] text-slate-500 mt-2 italic">
             Allocated per concurrent thread
           </div>
        </div>

        <div className="flex gap-2">
          <div className="bg-slate-800 p-3 rounded flex-1 text-center border border-slate-700">
             <div className="text-[10px] text-slate-500 uppercase">Block Size (r)</div>
             <div className="font-mono text-slate-300 font-bold">{params.r}</div>
          </div>
          <div className="bg-slate-800 p-3 rounded flex-1 text-center border border-slate-700">
             <div className="text-[10px] text-slate-500 uppercase">Parallel (p)</div>
             <div className="font-mono text-slate-300 font-bold">{params.p}</div>
          </div>
        </div>
      </div>
    </div>
  );
};
