import React, { useState, useEffect } from 'react';

export const SchemaRegistry: React.FC = () => {
  const [validations, setValidations] = useState<{id: string, ms: number, valid: boolean}[]>([]);

  useEffect(() => {
    let t = 0;
    const interval = setInterval(() => {
      t++;
      
      // Deterministic validation simulation
      const isValid = t % 6 !== 0; // 1 out of 6 fails
      const ms = 2 + Math.random() * 3; // 2-5ms simulated latency
      
      setValidations(prev => {
        const next = [{ id: `REQ_${t.toString().padStart(5, '0')}`, ms, valid: isValid }, ...prev];
        return next.slice(0, 8); // keep last 8
      });

    }, 400);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-2xl max-w-lg mx-auto font-sans">
      <div className="mb-6 flex justify-between items-center border-b border-slate-700 pb-3">
        <div>
          <h2 className="text-xl font-bold text-fuchsia-500">Pydantic Core</h2>
          <p className="text-xs text-slate-400">High-throughput Payload Validation</p>
        </div>
        <div className="flex flex-col items-end">
          <div className="text-xs font-mono text-emerald-400">Avg Latency: ~3.5ms</div>
          <div className="text-[10px] text-slate-500">Rust FFI active</div>
        </div>
      </div>

      <div className="flex flex-col gap-2">
        {validations.map(v => (
          <div key={v.id} className="bg-slate-800 p-3 rounded flex justify-between items-center border border-slate-700">
            <div className="flex items-center gap-3">
              <div className={`w-2 h-2 rounded-full ${v.valid ? 'bg-emerald-500' : 'bg-rose-500'}`}></div>
              <div className="font-mono text-xs text-slate-300">{v.id}</div>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="text-[10px] font-mono text-slate-500">{v.ms.toFixed(1)}ms</div>
              <div className={`text-[10px] font-bold px-2 py-1 rounded w-16 text-center
                ${v.valid ? 'bg-emerald-900/50 text-emerald-400' : 'bg-rose-900/50 text-rose-400'}
              `}>
                {v.valid ? 'OK' : 'ERROR'}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
