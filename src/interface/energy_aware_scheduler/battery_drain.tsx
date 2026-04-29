import React, { useState, useEffect } from 'react';

export const BatteryDrain: React.FC = () => {
  const [battery, setBattery] = useState(85);
  const [mode, setMode] = useState('HIGH_PERFORMANCE');

  useEffect(() => {
    const interval = setInterval(() => {
      setBattery(prev => {
        const drop = mode === 'HIGH_PERFORMANCE' ? 2 : mode === 'BALANCED' ? 0.8 : 0.2;
        const next = prev - drop;
        
        if (next < 20) setMode('POWER_SAVE');
        else if (next < 50) setMode('BALANCED');
        
        if (next <= 0) {
           clearInterval(interval);
           return 0;
        }
        return next;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [mode]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 border-b border-slate-700 pb-2">
        <h2 className="text-xl font-bold text-green-400">Energy Scheduler</h2>
        <p className="text-xs text-slate-400">Mobile Edge Inference</p>
      </div>

      <div className="flex items-center gap-4 mb-6">
         {/* Battery Icon */}
         <div className="w-16 h-8 border-2 border-slate-500 rounded relative p-0.5">
            <div className="absolute -right-2 top-2 w-1.5 h-3 bg-slate-500 rounded-r"></div>
            <div 
              className={`h-full rounded-sm transition-all duration-1000 ${battery > 50 ? 'bg-green-500' : battery > 20 ? 'bg-yellow-500' : 'bg-red-500'}`}
              style={{ width: `${Math.max(0, battery)}%` }}
            ></div>
         </div>
         <div className="text-2xl font-mono font-bold">{Math.max(0, battery).toFixed(0)}%</div>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 space-y-3">
         <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400">AI Exec Mode:</span>
            <span className={`px-2 py-1 rounded font-bold text-[10px] uppercase
               ${mode === 'HIGH_PERFORMANCE' ? 'bg-green-900/50 text-green-400 border border-green-800' : 
                 mode === 'BALANCED' ? 'bg-yellow-900/50 text-yellow-400 border border-yellow-800' : 
                 'bg-red-900/50 text-red-400 border border-red-800'}
            `}>{mode.replace('_', ' ')}</span>
         </div>
         
         <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400">Tokens/Sec:</span>
            <span className="font-mono text-white">
               {mode === 'HIGH_PERFORMANCE' ? '18.4' : mode === 'BALANCED' ? '8.2' : '2.1'}
            </span>
         </div>
         
         <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400">Est. Hardware Power:</span>
            <span className="font-mono text-white">
               {mode === 'HIGH_PERFORMANCE' ? '14.5 W' : mode === 'BALANCED' ? '4.8 W' : '1.2 W'}
            </span>
         </div>
      </div>
    </div>
  );
};
