import React, { useState, useEffect } from 'react';

export const ChannelMonitor: React.FC = () => {
  const [streams, setStreams] = useState<{id: string, rpc: string, deadline: number}[]>([]);

  useEffect(() => {
    let idCounter = 0;
    const interval = setInterval(() => {
      idCounter++;
      
      const rpcs = ['GetUser', 'ListOrders', 'UpdateProfile', 'StreamLogs'];
      const rpc = rpcs[idCounter % rpcs.length];
      
      const newStream = {
        id: `0x${idCounter.toString(16).padStart(4, '0').toUpperCase()}`,
        rpc,
        deadline: 5000 // ms
      };
      
      setStreams(prev => {
        const updated = prev.map(s => ({...s, deadline: s.deadline - 500})).filter(s => s.deadline > 0);
        if (Math.random() > 0.3) {
          return [newStream, ...updated].slice(0, 5);
        }
        return updated;
      });
      
    }, 500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-950 p-6 rounded-lg border border-slate-800 shadow-xl max-w-lg mx-auto font-sans text-slate-200">
      <div className="mb-6 flex justify-between items-center border-b border-slate-800 pb-3">
        <div>
          <h2 className="text-xl font-bold text-sky-500">gRPC Channel</h2>
          <p className="text-xs text-slate-400">HTTP/2 Stream Multiplexer</p>
        </div>
        <div className="text-[10px] font-mono bg-slate-900 px-2 py-1 rounded border border-slate-700">
          HPACK DELTA COMPRESSED
        </div>
      </div>

      <div className="flex flex-col gap-2">
        {streams.map(s => (
          <div key={s.id} className="bg-slate-900 p-3 rounded flex justify-between items-center border border-slate-800">
            <div className="flex items-center gap-3">
              <div className="font-mono text-xs text-sky-500 font-bold w-12">{s.id}</div>
              <div className="text-sm font-bold text-slate-300">{s.rpc}</div>
            </div>
            
            <div className="flex items-center gap-2 w-32">
              <div className="h-1.5 bg-slate-800 rounded-full w-full overflow-hidden">
                <div className={`h-full transition-all duration-300
                  ${s.deadline < 1500 ? 'bg-rose-500' : 'bg-sky-500'}
                `} style={{width: `${(s.deadline / 5000) * 100}%`}}></div>
              </div>
              <div className="text-[10px] font-mono text-slate-500 w-10 text-right">
                {s.deadline}ms
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
