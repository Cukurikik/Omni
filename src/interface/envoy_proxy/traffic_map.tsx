import React, { useState, useEffect } from 'react';

export const TrafficMap: React.FC = () => {
  const [nodes, setNodes] = useState<{id: string, requests: number, healthy: boolean}[]>([
    { id: '10.0.1.15', requests: 0, healthy: true },
    { id: '10.0.1.16', requests: 0, healthy: true },
    { id: '10.0.1.17', requests: 0, healthy: true }
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      setNodes(prev => prev.map((n, i) => {
        // Deterministic outlier ejection simulation
        if (i === 2 && Math.random() > 0.9) {
          return { ...n, healthy: false };
        }
        if (i === 2 && !n.healthy && Math.random() > 0.8) {
          return { ...n, healthy: true }; // Recovers
        }

        // Add traffic if healthy
        const add = n.healthy ? Math.floor(Math.random() * 50) : 0;
        return { ...n, requests: n.requests + add };
      }));
    }, 500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-lg mx-auto font-sans">
      <div className="mb-6 flex justify-between items-center border-b border-slate-700 pb-3">
        <div>
          <h2 className="text-xl font-bold text-fuchsia-500">Envoy L7 Proxy</h2>
          <p className="text-xs text-slate-400">Upstream Cluster Traffic Map</p>
        </div>
      </div>

      <div className="relative pt-12 pb-4">
        {/* Load Balancer Node */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 bg-fuchsia-600 text-white text-xs font-bold px-4 py-2 rounded shadow-lg z-10 border border-fuchsia-400">
          Envoy LB
        </div>

        {/* Lines */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 0 }}>
          {nodes.map((n, i) => {
            const x = 16.66 + (i * 33.33); // 16%, 50%, 83%
            return (
              <line 
                key={i} 
                x1="50%" y1="20" 
                x2={`${x}%`} y2="80" 
                stroke={n.healthy ? '#d946ef' : '#475569'} 
                strokeWidth={n.healthy ? 2 : 1} 
                strokeDasharray={n.healthy ? '0' : '4'}
                className="transition-all duration-300"
              />
            );
          })}
        </svg>

        {/* Upstream Nodes */}
        <div className="flex justify-between relative z-10 mt-16 px-4">
          {nodes.map((n, i) => (
            <div key={n.id} className="flex flex-col items-center">
               <div className={`w-12 h-12 rounded flex items-center justify-center border shadow-md transition-all duration-300
                 ${n.healthy ? 'bg-slate-800 border-fuchsia-500/50' : 'bg-slate-900 border-red-500/50 grayscale'}
               `}>
                 <svg className={`w-6 h-6 ${n.healthy ? 'text-fuchsia-400' : 'text-red-500'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                   <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01"></path>
                 </svg>
               </div>
               <div className="mt-2 text-[10px] font-mono text-slate-300">{n.id}</div>
               <div className="text-[10px] text-fuchsia-400 font-bold mt-1">{n.requests} Req</div>
               
               {!n.healthy && (
                 <div className="absolute -bottom-6 bg-red-900/80 text-red-200 text-[9px] px-1.5 py-0.5 rounded border border-red-700">
                   EJECTED
                 </div>
               )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
