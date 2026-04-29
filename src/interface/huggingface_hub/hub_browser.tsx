import React, { useState, useEffect } from 'react';

export const HubBrowser: React.FC = () => {
  const [models, setModels] = useState<{id: string, downloads: number, status: string}[]>([]);

  useEffect(() => {
    // Deterministic Hub State
    const initial = [
      { id: 'meta-llama/Llama-3-8B', downloads: 1450000, status: 'CACHED' },
      { id: 'mistralai/Mistral-7B', downloads: 890000, status: 'CACHED' },
      { id: 'Qwen/Qwen1.5-14B', downloads: 340000, status: 'ONLINE' },
      { id: 'google/gemma-2b', downloads: 560000, status: 'ONLINE' }
    ];
    setModels(initial);

    const interval = setInterval(() => {
      setModels(prev => prev.map(m => {
        if (m.status === 'ONLINE' && Math.random() > 0.8) {
          return { ...m, status: 'DOWNLOADING' };
        }
        if (m.status === 'DOWNLOADING' && Math.random() > 0.6) {
          return { ...m, status: 'CACHED' };
        }
        return m;
      }));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const getStatusStyle = (status: string) => {
    switch(status) {
      case 'CACHED': return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      case 'DOWNLOADING': return 'bg-sky-100 text-sky-800 border-sky-200 animate-pulse';
      case 'ONLINE': return 'bg-slate-100 text-slate-600 border-slate-200';
      default: return '';
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-xl max-w-lg mx-auto font-sans">
      <div className="mb-6 flex justify-between items-center border-b border-slate-100 pb-4">
        <div className="flex items-center gap-3">
          <div className="w-6 h-6 bg-yellow-400 rounded-full flex items-center justify-center font-bold text-white text-xs">H</div>
          <div>
            <h2 className="text-lg font-bold text-slate-800">Model Hub</h2>
            <p className="text-xs text-slate-500">Registry & Cache Manager</p>
          </div>
        </div>
        <div className="text-xs bg-slate-100 px-3 py-1 rounded-full font-mono text-slate-600">
          Cache: 14.2 GB
        </div>
      </div>

      <div className="flex flex-col gap-3">
        {models.map((m, i) => (
          <div key={i} className="flex justify-between items-center p-3 rounded border border-slate-100 hover:shadow-md transition-shadow group">
            <div>
              <div className="font-bold text-slate-700 text-sm group-hover:text-sky-600 transition-colors">{m.id}</div>
              <div className="text-xs text-slate-400 font-mono mt-1">
                {m.downloads.toLocaleString()} DLs
              </div>
            </div>
            <div className={`text-[10px] font-bold px-2 py-1 rounded border ${getStatusStyle(m.status)}`}>
              {m.status}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
