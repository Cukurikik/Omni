import React, { useState, useEffect } from 'react';

export const StreamMonitor: React.FC = () => {
  const [streams, setStreams] = useState<{id: number, cwnd: number, phase: string}[]>([
    { id: 1, cwnd: 10, phase: 'SLOW_START' },
    { id: 2, cwnd: 10, phase: 'SLOW_START' },
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      setStreams(prev => prev.map(s => {
        let newCwnd = s.cwnd;
        let newPhase = s.phase;

        // Packet Loss simulation (2% chance)
        if (Math.random() > 0.98) {
          newCwnd = Math.max(2, Math.floor(newCwnd / 2));
          newPhase = 'CONGESTION_AVOIDANCE';
        } else {
          if (newPhase === 'SLOW_START') {
            newCwnd = Math.min(100, newCwnd * 1.5); // Exponential growth
            if (newCwnd >= 64) newPhase = 'CONGESTION_AVOIDANCE';
          } else {
            newCwnd = Math.min(100, newCwnd + 2); // Linear growth
          }
        }

        return { ...s, cwnd: newCwnd, phase: newPhase };
      }));
    }, 400);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 flex justify-between items-center border-b border-slate-700 pb-3">
        <div>
          <h2 className="text-xl font-bold text-indigo-400">QUIC Transport</h2>
          <p className="text-xs text-slate-400">HTTP/3 Stream Multiplexer</p>
        </div>
        <div className="text-[10px] font-bold text-slate-900 bg-emerald-500 px-2 py-1 rounded shadow-[0_0_8px_#10b981]">
          0-RTT ACTIVE
        </div>
      </div>

      <div className="flex flex-col gap-4">
        {streams.map(s => (
          <div key={s.id} className="bg-slate-800 p-3 rounded border border-slate-700">
            <div className="flex justify-between items-center mb-2">
               <div className="font-mono text-sm font-bold text-slate-300">Stream 0x{s.id.toString(16).padStart(4, '0')}</div>
               <div className={`text-[9px] font-bold px-1.5 py-0.5 rounded
                 ${s.phase === 'SLOW_START' ? 'bg-indigo-900/50 text-indigo-400' : 'bg-amber-900/50 text-amber-400'}
               `}>
                 {s.phase}
               </div>
            </div>
            
            <div className="text-[9px] text-slate-500 mb-1 uppercase tracking-wider">Congestion Window (cwnd)</div>
            <div className="flex items-center gap-2">
               <div className="h-1.5 bg-slate-900 flex-1 rounded overflow-hidden">
                 <div className="h-full bg-indigo-500 transition-all duration-300" style={{width: `${s.cwnd}%`}}></div>
               </div>
               <div className="font-mono text-xs w-8 text-right text-slate-400">{Math.floor(s.cwnd)}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
