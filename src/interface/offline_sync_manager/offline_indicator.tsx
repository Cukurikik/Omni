import React, { useState, useEffect } from 'react';

export const OfflineIndicator: React.FC = () => {
  const [isOnline, setIsOnline] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [pendingQueue, setPendingQueue] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setIsOnline(prev => {
        // Randomly drop connection
        const online = Math.random() > 0.3;
        
        if (!online) {
           setPendingQueue(q => q + 1);
           setSyncing(false);
        } else if (online && !prev) {
           // Just reconnected
           setSyncing(true);
           setTimeout(() => {
              setSyncing(false);
              setPendingQueue(0);
           }, 1500);
        }
        return online;
      });
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-blue-400">Edge Sync</h2>
          <p className="text-xs text-slate-400">CRDT Offline Manager</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-bold uppercase border ${isOnline ? 'bg-emerald-900/50 text-emerald-400 border-emerald-800' : 'bg-slate-800 text-slate-400 border-slate-600'}`}>
           {isOnline ? 'Online' : 'Offline'}
        </div>
      </div>

      <div className="bg-slate-950 p-6 rounded border border-slate-800 flex flex-col items-center justify-center mb-4 min-h-[140px]">
         {syncing ? (
            <div className="flex flex-col items-center animate-fade-in">
               <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-3"></div>
               <div className="text-xs text-blue-400 font-mono">Syncing {pendingQueue} operations...</div>
            </div>
         ) : isOnline ? (
            <div className="flex flex-col items-center animate-fade-in">
               <div className="text-4xl mb-2 text-emerald-500">☁️</div>
               <div className="text-xs text-slate-400 font-mono">Cloud Synced (CRDT Match)</div>
            </div>
         ) : (
            <div className="flex flex-col items-center animate-fade-in">
               <div className="text-4xl mb-2 text-slate-600 grayscale">📱</div>
               <div className="text-xs text-amber-400 font-mono">Local Cache Active</div>
               <div className="text-[10px] text-slate-500 mt-1">Pending Mutations: {pendingQueue}</div>
            </div>
         )}
      </div>
    </div>
  );
};
