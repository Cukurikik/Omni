import React, { useState, useEffect } from 'react';

export const LoadBalancerDashboard: React.FC = () => {
  const [backends, setBackends] = useState<{name: string, conns: number, bytesIn: number, bytesOut: number}[]>([
    { name: 'app_backend_1', conns: 120, bytesIn: 5400, bytesOut: 45000 },
    { name: 'app_backend_2', conns: 118, bytesIn: 5200, bytesOut: 44200 },
    { name: 'app_backend_3', conns: 122, bytesIn: 5600, bytesOut: 46100 },
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      setBackends(prev => prev.map(b => {
        // Deterministic Least Connections simulation
        // The one with least connections gets the most new ones
        
        let deltaConn = Math.floor(Math.random() * 10) - 4; // -4 to +5
        
        const newConns = Math.max(0, b.conns + deltaConn);
        const newBytesIn = b.bytesIn + (newConns * 10);
        const newBytesOut = b.bytesOut + (newConns * 80);

        return { ...b, conns: newConns, bytesIn: newBytesIn, bytesOut: newBytesOut };
      }));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-2xl mx-auto font-sans text-slate-200">
      <div className="mb-6 flex justify-between items-center border-b border-slate-700 pb-3">
        <div>
          <h2 className="text-xl font-bold text-amber-500">HAProxy</h2>
          <p className="text-xs text-slate-400">LeastConn Backend Topology</p>
        </div>
        <div className="text-[10px] font-mono bg-emerald-900/50 text-emerald-400 px-2 py-1 rounded border border-emerald-800">
          epoll() EDGE TRIGGERED
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {backends.map((b, i) => (
          <div key={b.name} className="bg-slate-800 p-4 rounded border border-slate-700 shadow-sm flex flex-col gap-3">
            <div className="font-bold text-slate-300 text-sm border-b border-slate-700 pb-2 flex justify-between">
              {b.name}
              <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
            </div>
            
            <div>
              <div className="text-[10px] text-slate-500 uppercase font-bold tracking-wider mb-1">Active Conns</div>
              <div className="text-2xl font-mono font-black text-amber-500">{b.conns}</div>
            </div>

            <div className="flex justify-between mt-2 pt-2 border-t border-slate-700">
              <div>
                <div className="text-[9px] text-slate-500 uppercase">Bytes In</div>
                <div className="text-xs font-mono text-emerald-400">{(b.bytesIn / 1024).toFixed(1)}K</div>
              </div>
              <div className="text-right">
                <div className="text-[9px] text-slate-500 uppercase">Bytes Out</div>
                <div className="text-xs font-mono text-blue-400">{(b.bytesOut / 1024).toFixed(1)}K</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
