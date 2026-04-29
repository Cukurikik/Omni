import React, { useState, useEffect } from 'react';

export const LineageTree: React.FC = () => {
  const [stages, setStages] = useState<{name: string, status: string, hash: string}[]>([]);

  useEffect(() => {
    // Deterministic DVC pipeline DAG
    const dvcStages = [
      { name: 'data_extract', status: 'CACHED', hash: 'a1b2c3d' },
      { name: 'data_clean', status: 'CACHED', hash: 'f4g5h6j' },
      { name: 'feature_eng', status: 'RUNNING', hash: '...' },
      { name: 'model_train', status: 'QUEUED', hash: '...' },
      { name: 'model_eval', status: 'QUEUED', hash: '...' }
    ];
    setStages(dvcStages);

    const interval = setInterval(() => {
      setStages(prev => prev.map((s, i) => {
        if (s.name === 'feature_eng' && s.status === 'RUNNING') {
          return { ...s, status: 'CACHED', hash: 'k7l8m9n' };
        }
        if (s.name === 'model_train' && prev[i-1].status === 'CACHED' && s.status === 'QUEUED') {
          return { ...s, status: 'RUNNING' };
        }
        return s;
      }));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg shadow-xl border border-slate-700 max-w-md mx-auto font-sans text-slate-200">
      <div className="mb-6 flex justify-between items-center border-b border-slate-700 pb-3">
        <div>
          <h2 className="text-xl font-bold text-emerald-500">DVC Lineage</h2>
          <p className="text-xs text-slate-400">Data & Code Dependency Tree</p>
        </div>
      </div>

      <div className="relative border-l-2 border-slate-700 ml-4 py-2 flex flex-col gap-6">
        {stages.map((stage, i) => (
          <div key={i} className="relative pl-6">
            <div className={`absolute -left-[9px] top-1 w-4 h-4 rounded-full border-4 border-slate-900
              ${stage.status === 'CACHED' ? 'bg-emerald-500' : 
                stage.status === 'RUNNING' ? 'bg-amber-400 animate-pulse' : 'bg-slate-600'}
            `}></div>
            
            <div className="bg-slate-800 p-3 rounded border border-slate-700 shadow flex justify-between items-center">
              <div>
                <div className="text-sm font-bold text-slate-300">{stage.name}</div>
                <div className="text-[10px] text-slate-500 font-mono mt-1">MD5: {stage.hash}</div>
              </div>
              <div className={`text-[9px] font-bold px-2 py-1 rounded 
                ${stage.status === 'CACHED' ? 'bg-emerald-900/50 text-emerald-400' : 
                  stage.status === 'RUNNING' ? 'bg-amber-900/50 text-amber-400' : 'bg-slate-700 text-slate-400'}
              `}>
                {stage.status}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
