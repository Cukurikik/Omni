import React, { useState, useEffect } from 'react';

export const TopologyMap: React.FC = () => {
  const [workers, setWorkers] = useState<{id: string, active: boolean, load: number}[]>([
    { id: 'worker-node-1', active: true, load: 45 },
    { id: 'worker-node-2', active: true, load: 82 },
    { id: 'worker-node-3', active: false, load: 0 },
    { id: 'worker-node-4', active: true, load: 12 }
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      setWorkers(prev => prev.map(w => {
        if (!w.active) {
          // Chance to come online
          if (Math.random() > 0.9) return { ...w, active: true, load: 10 };
          return w;
        }
        
        // Fluctuate load deterministically
        let newLoad = w.load + (Math.random() > 0.5 ? 15 : -15);
        newLoad = Math.max(0, Math.min(100, newLoad));
        
        // Chance to crash
        if (newLoad === 100 && Math.random() > 0.8) return { ...w, active: false, load: 0 };
        
        return { ...w, load: newLoad };
      }));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-950 p-6 rounded-lg border border-slate-800 shadow-xl max-w-lg mx-auto font-sans text-slate-200">
      <div className="mb-6 flex justify-between items-center border-b border-slate-800 pb-3">
        <div>
          <h2 className="text-xl font-bold text-lime-500">Celery Distributed</h2>
          <p className="text-xs text-slate-400">Worker Node Topology</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {workers.map(w => (
          <div key={w.id} className="bg-slate-900 border border-slate-700 rounded p-4 flex flex-col gap-3">
            <div className="flex justify-between items-center">
              <div className="font-mono text-xs font-bold">{w.id}</div>
              <div className={`w-2.5 h-2.5 rounded-full ${w.active ? 'bg-lime-500 shadow-[0_0_8px_#84cc16]' : 'bg-rose-600'}`}></div>
            </div>
            
            <div className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">CPU Load</div>
            
            <div className="h-2 bg-slate-800 rounded overflow-hidden">
              <div className={`h-full transition-all duration-300 ${
                w.load > 80 ? 'bg-rose-500' : w.load > 50 ? 'bg-amber-500' : 'bg-lime-500'
              }`} style={{width: `${w.load}%`}}></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
