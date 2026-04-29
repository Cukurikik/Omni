import React, { useState, useEffect } from 'react';

export const RouteTopology: React.FC = () => {
  const [requests, setRequests] = useState<{id: string, path: string, method: string, status: number}[]>([]);

  useEffect(() => {
    let t = 0;
    const interval = setInterval(() => {
      t++;
      const paths = ['/api/v1/users', '/api/v1/posts', '/health', '/api/v1/auth'];
      const methods = ['GET', 'POST', 'GET', 'POST'];
      const idx = t % paths.length;
      
      setRequests(prev => {
        const next = [{ 
          id: `req_${t.toString().padStart(4, '0')}`, 
          path: paths[idx], 
          method: methods[idx],
          status: Math.random() > 0.95 ? 500 : 200 // 5% error rate simulation
        }, ...prev];
        return next.slice(0, 8);
      });
    }, 300);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-2xl max-w-lg mx-auto font-sans">
      <div className="mb-6 flex justify-between items-center border-b border-slate-700 pb-3">
        <div>
          <h2 className="text-xl font-bold text-emerald-400">FastAPI Router</h2>
          <p className="text-xs text-slate-400">Live Request Multiplexing</p>
        </div>
        <div className="flex gap-2">
           <span className="text-[10px] font-mono bg-emerald-900/50 text-emerald-400 px-2 py-1 rounded border border-emerald-800">
             Uvicorn: ONLINE
           </span>
        </div>
      </div>

      <div className="flex flex-col gap-2">
        {requests.map(req => (
          <div key={req.id} className="bg-slate-800 p-3 rounded flex justify-between items-center border border-slate-700">
            <div className="flex items-center gap-3">
              <div className={`text-[10px] font-bold px-2 py-1 rounded w-12 text-center
                ${req.method === 'GET' ? 'bg-blue-900/50 text-blue-400' : 'bg-green-900/50 text-green-400'}
              `}>
                {req.method}
              </div>
              <div className="font-mono text-sm text-slate-300 font-bold">{req.path}</div>
            </div>
            
            <div className="flex items-center gap-4">
              <div className={`text-[10px] font-bold px-2 py-1 rounded text-center
                ${req.status === 200 ? 'bg-emerald-900/50 text-emerald-400' : 'bg-rose-900/50 text-rose-400'}
              `}>
                {req.status}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
