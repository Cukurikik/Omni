import React, { useState, useEffect } from 'react';

export const SequenceDiagram: React.FC = () => {
  const [logs, setLogs] = useState<{id: number, type: string, value: string}[]>([]);

  useEffect(() => {
    let tick = 0;
    const interval = setInterval(() => {
      tick++;
      
      const phase = tick % 4;
      let type = '';
      let value = '';

      if (phase === 1) { type = 'PREPARE'; value = `Round ${tick}`; }
      else if (phase === 2) { type = 'PROMISE'; value = `Majority Quorum`; }
      else if (phase === 3) { type = 'ACCEPT'; value = `State_V${Math.floor(tick/4)}`; }
      else { type = 'ACCEPTED'; value = 'WAL Synced'; }

      setLogs(prev => {
        const next = [{ id: tick, type, value }, ...prev];
        return next.slice(0, 6);
      });

    }, 800);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-950 p-6 rounded-lg border border-slate-800 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 border-b border-slate-800 pb-2">
        <h2 className="text-xl font-bold text-indigo-400">Paxos Consensus</h2>
        <p className="text-xs text-slate-400">Distributed State Machine Flow</p>
      </div>

      <div className="flex justify-between text-[10px] font-bold text-slate-500 uppercase border-b border-slate-800 pb-2 mb-4">
        <div className="w-16 text-center">Proposer</div>
        <div className="flex-1 text-center">Network</div>
        <div className="w-16 text-center">Acceptors</div>
      </div>

      <div className="flex flex-col gap-3">
        {logs.map((l, i) => {
          const isProposer = l.type === 'PREPARE' || l.type === 'ACCEPT';
          return (
            <div key={l.id} className="flex items-center text-xs">
              <div className="w-16 flex justify-center">
                {isProposer && <div className="w-2 h-2 rounded-full bg-indigo-500"></div>}
              </div>
              
              <div className="flex-1 relative flex items-center justify-center">
                <div className="absolute inset-0 flex items-center">
                  <div className={`h-0.5 w-full ${isProposer ? 'bg-indigo-900' : 'bg-emerald-900'}`}></div>
                </div>
                <div className={`relative z-10 px-2 py-0.5 rounded font-bold font-mono text-[9px] border
                  ${isProposer ? 'bg-slate-900 border-indigo-700 text-indigo-300' : 'bg-slate-900 border-emerald-700 text-emerald-300'}
                `}>
                  {l.type}: {l.value}
                </div>
              </div>

              <div className="w-16 flex justify-center">
                {!isProposer && <div className="w-2 h-2 rounded-full bg-emerald-500"></div>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
