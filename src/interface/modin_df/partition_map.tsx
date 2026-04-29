import React, { useState, useEffect } from 'react';

export const PartitionMap: React.FC = () => {
  const [partitions, setPartitions] = useState<{id: number, status: string, progress: number}[]>(
    Array.from({length: 8}, (_, i) => ({ id: i, status: 'IDLE', progress: 0 }))
  );

  useEffect(() => {
    const interval = setInterval(() => {
      setPartitions(prev => {
        let allDone = true;
        const next = prev.map(p => {
          if (p.progress < 100) {
            allDone = false;
            // Deterministic asynchronous execution simulation
            const increment = Math.random() > 0.3 ? 10 : 0;
            const nextProg = Math.min(100, p.progress + increment);
            return {
              ...p,
              progress: nextProg,
              status: nextProg === 100 ? 'COMPUTED' : (nextProg > 0 ? 'COMPUTING' : 'IDLE')
            };
          }
          return p;
        });

        if (allDone) clearInterval(interval);
        return next;
      });
    }, 300);

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch(status) {
      case 'IDLE': return 'bg-slate-700';
      case 'COMPUTING': return 'bg-blue-500';
      case 'COMPUTED': return 'bg-emerald-500';
      default: return 'bg-slate-500';
    }
  };

  return (
    <div className="bg-slate-900 p-6 rounded-xl shadow-2xl max-w-2xl mx-auto font-sans text-slate-100 border border-slate-800">
      <div className="mb-6 flex justify-between items-center border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-xl font-bold text-blue-400">Modin DataFrames</h2>
          <p className="text-xs text-slate-400">Distributed Partition Engine</p>
        </div>
        <div className="text-xs bg-slate-800 px-3 py-1 rounded font-mono shadow-inner">
          Total Memory: 1.2 GB
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4">
        {partitions.map(p => (
          <div key={p.id} className="bg-slate-800 rounded p-4 border border-slate-700 flex flex-col items-center shadow-lg">
            <div className="text-sm font-bold text-slate-300 mb-2">Partition {p.id}</div>
            
            {/* Progress Circle */}
            <div className="relative w-12 h-12 mb-3">
              <svg className="w-full h-full transform -rotate-90">
                <circle cx="24" cy="24" r="20" stroke="currentColor" strokeWidth="4" fill="transparent" className="text-slate-700" />
                <circle 
                  cx="24" cy="24" r="20" stroke="currentColor" strokeWidth="4" fill="transparent" 
                  className={`${getStatusColor(p.status).replace('bg-', 'text-')} transition-all duration-300`}
                  strokeDasharray="125.6"
                  strokeDashoffset={125.6 - (p.progress / 100) * 125.6}
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center text-[10px] font-bold">
                {p.progress}%
              </div>
            </div>

            <div className={`text-[9px] font-bold px-2 py-1 rounded ${getStatusColor(p.status)} shadow-sm`}>
              {p.status}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
