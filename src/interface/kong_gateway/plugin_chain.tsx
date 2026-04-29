import React, { useState, useEffect } from 'react';

export const PluginChain: React.FC = () => {
  const [pipeline, setPipeline] = useState<{name: string, status: string, ms: number}[]>([
    { name: 'auth-jwt', status: 'OK', ms: 2 },
    { name: 'rate-limiting', status: 'OK', ms: 1 },
    { name: 'request-transformer', status: 'OK', ms: 3 },
    { name: 'prometheus', status: 'OK', ms: 1 }
  ]);

  const [reqCount, setReqCount] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setReqCount(c => c + 1);
      
      setPipeline(prev => prev.map(p => {
        // Deterministic simulation of occasional plugin latency/failure
        const newMs = Math.max(1, p.ms + (Math.random() > 0.5 ? 1 : -1));
        
        let newStatus = 'OK';
        if (p.name === 'auth-jwt' && Math.random() > 0.95) newStatus = '401';
        if (p.name === 'rate-limiting' && Math.random() > 0.95) newStatus = '429';

        return { ...p, ms: newMs, status: newStatus };
      }));
    }, 400);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans">
      <div className="mb-6 flex justify-between items-center border-b border-slate-700 pb-3">
        <div>
          <h2 className="text-xl font-bold text-teal-500">Kong Gateway</h2>
          <p className="text-xs text-slate-400">LuaJIT Plugin Execution Pipeline</p>
        </div>
        <div className="text-[10px] font-mono text-slate-400 bg-slate-800 px-2 py-1 rounded">
          Reqs: {reqCount}
        </div>
      </div>

      <div className="flex flex-col gap-1 relative">
        {/* Pipeline connecting line */}
        <div className="absolute left-6 top-4 bottom-4 w-0.5 bg-slate-700 z-0"></div>

        {pipeline.map((p, i) => (
          <div key={p.name} className="relative z-10 flex items-center gap-4 bg-slate-800/80 p-3 rounded border border-slate-700 backdrop-blur-sm">
            <div className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold border-2
              ${p.status === 'OK' ? 'bg-slate-900 border-teal-500 text-teal-500' : 'bg-rose-900 border-rose-500 text-rose-200'}
            `}>
              {i + 1}
            </div>
            
            <div className="flex-1">
              <div className="font-bold text-slate-300 text-sm">{p.name}</div>
            </div>
            
            <div className="flex flex-col items-end">
              <div className={`text-[10px] font-bold px-1.5 py-0.5 rounded
                ${p.status === 'OK' ? 'text-teal-400 bg-teal-900/30' : 'text-rose-400 bg-rose-900/30'}
              `}>
                {p.status}
              </div>
              <div className="text-[10px] font-mono text-slate-500 mt-1">{p.ms}ms</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
