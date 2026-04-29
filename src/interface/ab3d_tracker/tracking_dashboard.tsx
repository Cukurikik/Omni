import React, { useState, useEffect } from 'react';

export const TrackingDashboard: React.FC = () => {
  const [tracks, setTracks] = useState<{id: number, x: number, y: number, state: string}[]>([
    { id: 1, x: 20, y: 30, state: 'CONFIRMED' },
    { id: 2, x: 80, y: 70, state: 'CONFIRMED' },
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      setTracks(prev => prev.map(t => {
        // Kalman filter prediction visual simulation
        const dx = (Math.random() - 0.5) * 4;
        const dy = (Math.random() - 0.5) * 4;
        
        let newState = t.state;
        if (Math.random() > 0.95) newState = 'COASTING'; // Missed detection
        if (t.state === 'COASTING' && Math.random() > 0.7) newState = 'CONFIRMED';

        return {
          ...t,
          x: Math.max(0, Math.min(100, t.x + dx)),
          y: Math.max(0, Math.min(100, t.y + dy)),
          state: newState
        };
      }));
    }, 100);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 flex justify-between items-center border-b border-slate-700 pb-3">
        <div>
          <h2 className="text-xl font-bold text-amber-500">AB3DMOT Tracker</h2>
          <p className="text-xs text-slate-400">3D Kalman Filter + Hungarian</p>
        </div>
      </div>

      <div className="relative w-full aspect-square bg-slate-950 rounded-lg border border-slate-800 overflow-hidden">
        {/* Radar grids */}
        <div className="absolute inset-0 border border-slate-800/50 m-4 rounded-full pointer-events-none"></div>
        <div className="absolute inset-0 border border-slate-800/50 m-12 rounded-full pointer-events-none"></div>
        <div className="absolute inset-0 border border-slate-800/50 m-20 rounded-full pointer-events-none"></div>
        <div className="absolute top-1/2 left-0 right-0 h-px bg-slate-800/50 pointer-events-none"></div>
        <div className="absolute left-1/2 top-0 bottom-0 w-px bg-slate-800/50 pointer-events-none"></div>

        {/* Tracks */}
        {tracks.map(t => (
          <div key={t.id} 
               className={`absolute w-3 h-3 -ml-1.5 -mt-1.5 rounded-full transition-all duration-100 shadow-[0_0_8px_currentColor]
                 ${t.state === 'CONFIRMED' ? 'bg-amber-400 text-amber-400' : 'bg-slate-500 text-slate-500 opacity-50'}
               `}
               style={{left: `${t.x}%`, top: `${t.y}%`}}>
            <div className="absolute left-4 top-0 text-[8px] font-mono font-bold">{t.id}</div>
          </div>
        ))}

        {/* Ego vehicle */}
        <div className="absolute top-1/2 left-1/2 w-2 h-3 bg-white -ml-1 -mt-1.5 rounded-sm"></div>
      </div>
    </div>
  );
};
