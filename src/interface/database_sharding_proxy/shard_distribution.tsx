import React, { useState, useEffect } from 'react';

export const ShardDistribution: React.FC = () => {
  const [shards, setShards] = useState<number[]>([20, 20, 20, 20, 20]); // 5 database shards

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate load distribution via Consistent Hashing
      setShards(prev => {
         return prev.map(load => {
            const fluctuation = (Math.random() * 10) - 5;
            return Math.max(5, Math.min(95, load + fluctuation));
         });
      });
    }, 800);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-emerald-400">DB Shard Proxy</h2>
          <p className="text-xs text-slate-400">Consistent Hashing Ring</p>
        </div>
        <div className="px-2 py-1 bg-emerald-900/30 text-emerald-400 text-[10px] font-mono rounded border border-emerald-800">
          PgBouncer L7
        </div>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 space-y-3 mb-4">
         {shards.map((load, index) => (
            <div key={index} className="flex items-center gap-3">
               <div className="w-8 text-[10px] font-mono text-slate-500">DB_{index}</div>
               <div className="flex-1 h-3 bg-slate-800 rounded-full overflow-hidden relative border border-slate-700">
                  <div 
                    className={`absolute top-0 bottom-0 left-0 transition-all duration-500
                      ${load > 85 ? 'bg-red-500' : load > 60 ? 'bg-yellow-500' : 'bg-emerald-500'}
                    `}
                    style={{ width: `${load}%` }}
                  ></div>
               </div>
               <div className="w-8 text-right text-[10px] font-mono text-white">{load.toFixed(0)}%</div>
            </div>
         ))}
      </div>
      
      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Client Conns: <span className="text-white">124,592</span></span>
         <span>Proxy Pools: <span className="text-emerald-400">500</span></span>
         <span className="col-span-2 text-center text-xs text-slate-500 mt-1 pt-1 border-t border-slate-700">
            Read/Write Split Active
         </span>
      </div>
    </div>
  );
};
