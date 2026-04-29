import React, { useState, useEffect } from 'react';

export const ParamViz: React.FC = () => {
  const [params, setParams] = useState({ m: 65536, t: 3, p: 4 }); // OWASP recommended approx
  const [computing, setComputing] = useState(false);
  const [hashTime, setHashTime] = useState(0);

  const simulateHash = () => {
    setComputing(true);
    
    // Simulate time based on params
    const timeMs = (params.m / 1024) * params.t * (2 / params.p) * 10;
    
    setTimeout(() => {
      setHashTime(Math.round(timeMs));
      setComputing(false);
    }, Math.min(timeMs, 2000)); // Cap simulation time so UI doesn't hang forever
  };

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 border-b border-slate-700 pb-2">
        <h2 className="text-xl font-bold text-sky-400">Argon2id KDF</h2>
        <p className="text-xs text-slate-400">OWASP Parameter Tuning</p>
      </div>

      <div className="flex flex-col gap-4 mb-6">
        <div>
          <div className="flex justify-between text-xs font-bold text-slate-400 mb-1">
             <span>Memory (m)</span>
             <span className="text-sky-400">{params.m / 1024} MiB</span>
          </div>
          <input type="range" min="19456" max="262144" step="1024" value={params.m} 
             onChange={e => setParams({...params, m: parseInt(e.target.value)})}
             className="w-full accent-sky-500" />
        </div>
        
        <div>
          <div className="flex justify-between text-xs font-bold text-slate-400 mb-1">
             <span>Iterations (t)</span>
             <span className="text-emerald-400">{params.t}</span>
          </div>
          <input type="range" min="2" max="10" step="1" value={params.t} 
             onChange={e => setParams({...params, t: parseInt(e.target.value)})}
             className="w-full accent-emerald-500" />
        </div>

        <div>
          <div className="flex justify-between text-xs font-bold text-slate-400 mb-1">
             <span>Parallel Lanes (p)</span>
             <span className="text-violet-400">{params.p}</span>
          </div>
          <input type="range" min="1" max="8" step="1" value={params.p} 
             onChange={e => setParams({...params, p: parseInt(e.target.value)})}
             className="w-full accent-violet-500" />
        </div>
      </div>

      <button 
        onClick={simulateHash}
        disabled={computing}
        className="w-full bg-sky-600 hover:bg-sky-500 text-white font-bold py-2 rounded transition-colors disabled:opacity-50"
      >
        {computing ? 'Computing Hash...' : 'Simulate Hash'}
      </button>

      {hashTime > 0 && !computing && (
        <div className="mt-4 text-center">
           <div className="text-[10px] text-slate-500 uppercase">Estimated Compute Time</div>
           <div className={`text-2xl font-mono font-black ${hashTime < 500 ? 'text-rose-500' : 'text-emerald-500'}`}>
             {hashTime} ms
           </div>
           {hashTime < 500 && (
             <div className="text-[10px] text-rose-400 mt-1">Warning: Too fast. Vulnerable to GPU brute force.</div>
           )}
        </div>
      )}
    </div>
  );
};
