import React, { useState, useEffect } from 'react';

export const PartitionDashboard: React.FC = () => {
  const [partitions, setPartitions] = useState<{id: number, hw: number, leo: number}[]>([
    { id: 0, hw: 1000, leo: 1005 },
    { id: 1, hw: 2540, leo: 2540 },
    { id: 2, hw: 300, leo: 312 },
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      setPartitions(prev => prev.map(p => {
        // LEO = Log End Offset (where producer writes)
        // HW = High Watermark (where consumer can safely read, replicated)
        
        const produce = Math.floor(Math.random() * 5);
        const replicate = Math.floor(Math.random() * 4);
        
        const newLeo = p.leo + produce;
        // HW catches up to LEO
        const newHw = Math.min(newLeo, p.hw + replicate);

        return { ...p, leo: newLeo, hw: newHw };
      }));
    }, 500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-lg mx-auto font-sans text-slate-200">
      <div className="mb-6 flex justify-between items-center border-b border-slate-700 pb-3">
        <div>
          <h2 className="text-xl font-bold text-orange-500">Kafka Broker</h2>
          <p className="text-xs text-slate-400">Partition Offset Tracking</p>
        </div>
        <div className="text-[10px] font-mono text-slate-400 bg-slate-800 px-2 py-1 rounded">
          ZERO-COPY mmap()
        </div>
      </div>

      <div className="flex flex-col gap-4">
        {partitions.map(p => {
          const lag = p.leo - p.hw;
          
          return (
            <div key={p.id} className="bg-slate-800 p-4 rounded border border-slate-700 shadow-sm relative overflow-hidden">
               <div className="flex justify-between items-center mb-3">
                 <div className="font-bold text-sm text-slate-300">Partition-{p.id}</div>
                 <div className={`text-[10px] font-bold px-2 py-0.5 rounded
                   ${lag === 0 ? 'bg-emerald-900/50 text-emerald-400' : 'bg-amber-900/50 text-amber-400'}
                 `}>
                   Lag: {lag}
                 </div>
               </div>

               {/* Log visualization */}
               <div className="h-4 bg-slate-900 rounded border border-slate-700 relative overflow-hidden flex">
                  {/* High Watermark - Data is replicated and readable */}
                  <div className="h-full bg-emerald-600 transition-all duration-300" 
                       style={{width: `${Math.min(100, (p.hw / (p.leo + 10)) * 100)}%`}}>
                  </div>
                  
                  {/* Unreplicated Data (Gap between HW and LEO) */}
                  <div className="h-full bg-orange-500/50 transition-all duration-300"
                       style={{width: `${Math.min(100, (lag / (p.leo + 10)) * 100)}%`}}>
                  </div>
               </div>
               
               <div className="flex justify-between mt-1 px-1">
                 <div className="text-[9px] font-mono text-emerald-400">HW: {p.hw}</div>
                 <div className="text-[9px] font-mono text-orange-400">LEO: {p.leo}</div>
               </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
