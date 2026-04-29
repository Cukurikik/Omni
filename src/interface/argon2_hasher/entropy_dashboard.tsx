import React, { useState, useEffect } from 'react';

export const EntropyDashboard: React.FC = () => {
  const [hashes, setHashes] = useState<{id: string, cost: number, ms: number}[]>([]);

  useEffect(() => {
    let t = 0;
    const interval = setInterval(() => {
      t++;
      
      // Simulating heavy hashing
      const ms = 200 + Math.random() * 100;
      
      setHashes(prev => {
        const next = [{ id: `USR_${t.toString().padStart(4, '0')}`, cost: 3, ms }, ...prev];
        return next.slice(0, 5); // keep last 5
      });

    }, 1500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-2xl max-w-lg mx-auto font-sans">
      <div className="mb-6 flex justify-between items-center border-b border-slate-700 pb-3">
        <div>
          <h2 className="text-xl font-bold text-violet-500">Argon2 KDF</h2>
          <p className="text-xs text-slate-400">Cryptographic Entropy Pool</p>
        </div>
        <div className="text-xs font-mono text-slate-500 bg-slate-800 px-2 py-1 rounded">
          Mem: 64MB | Iter: 3 | Parallel: 4
        </div>
      </div>

      <div className="flex flex-col gap-3">
        {hashes.map(h => (
          <div key={h.id} className="bg-slate-800 p-4 rounded border border-slate-700 flex justify-between items-center shadow-sm">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded bg-violet-900/50 flex items-center justify-center text-violet-400">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
                </svg>
              </div>
              <div>
                <div className="font-bold text-sm text-slate-300">{h.id}</div>
                <div className="text-[10px] text-slate-500 font-mono">Argon2id Hash Computed</div>
              </div>
            </div>
            
            <div className="text-right">
              <div className="text-[10px] font-bold text-slate-500 uppercase">Compute Time</div>
              <div className="text-sm font-mono font-bold text-emerald-400">
                {h.ms.toFixed(0)} ms
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
