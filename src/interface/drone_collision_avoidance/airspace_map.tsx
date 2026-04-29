import React, { useState, useEffect } from 'react';

export const AirspaceMap: React.FC = () => {
  const [egoY, setEgoY] = useState(150);
  const [intruderY, setIntruderY] = useState(-50);
  const [alert, setAlert] = useState(false);
  const [evading, setEvading] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      // Intruder drone moving south
      setIntruderY(prev => {
         const next = prev + 5;
         if (next > 250) return -50;
         return next;
      });
      
      // Ego drone moving north
      setEgoY(prev => {
         // If collision imminent, perform evasive maneuver (shift X axis implicitly by jumping)
         if (Math.abs(prev - intruderY) < 40 && !evading) {
            setAlert(true);
            setEvading(true);
            setTimeout(() => {
               setAlert(false);
               setEvading(false);
            }, 1000);
         }
         
         const next = prev - 3;
         if (next < -50) return 250;
         return next;
      });

    }, 50);
    return () => clearInterval(interval);
  }, [intruderY, evading]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-sky-400">UAV Radar</h2>
          <p className="text-xs text-slate-400">AABB Collision Avoidance</p>
        </div>
        {alert ? (
           <div className="px-2 py-1 bg-red-900/50 text-red-400 text-[10px] font-mono rounded border border-red-800 animate-pulse">
             TCAS ALERT
           </div>
        ) : (
           <div className="px-2 py-1 bg-emerald-900/30 text-emerald-400 text-[10px] font-mono rounded border border-emerald-800">
             AIRSPACE CLEAR
           </div>
        )}
      </div>

      <div className="bg-[#0f172a] p-0 rounded border border-slate-800 relative h-[200px] mb-4 overflow-hidden shadow-inner">
         
         {/* Radar grid lines */}
         <div className="absolute inset-0 grid grid-cols-4 grid-rows-4 opacity-20 pointer-events-none">
            {[...Array(16)].map((_, i) => <div key={i} className="border border-sky-500"></div>)}
         </div>

         {/* Intruder Drone (Red) */}
         <div 
            className="absolute w-6 h-6 border-2 border-red-500 bg-red-900/50 rounded shadow-[0_0_10px_#ef4444] flex items-center justify-center transition-all duration-75"
            style={{ top: `${intruderY}px`, left: '140px' }}
         >
            <div className="w-1 h-1 bg-white rounded-full animate-ping"></div>
            {/* AABB Box overlay when close */}
            {alert && <div className="absolute w-12 h-12 border border-red-400/50 -z-10"></div>}
         </div>

         {/* Ego Drone (Blue) */}
         <div 
            className={`absolute w-6 h-6 border-2 border-sky-500 bg-sky-900/50 rounded flex items-center justify-center transition-all duration-75
               ${alert ? 'shadow-[0_0_15px_#f59e0b] border-amber-500 bg-amber-900/50' : 'shadow-[0_0_10px_#0ea5e9]'}
            `}
            style={{ top: `${egoY}px`, left: evading ? '100px' : '140px' }}
         >
            <div className="w-1 h-1 bg-white rounded-full"></div>
            {/* AABB Box overlay when close */}
            {alert && <div className="absolute w-12 h-12 border border-amber-400/50 -z-10"></div>}
         </div>

      </div>
      
      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Alt: <span className="text-white">400ft (MSA: 200ft)</span></span>
         <span>Mode: <span className="text-emerald-400">Autonomous</span></span>
         <span className="col-span-2 text-sky-400">Telemetry: <span className="text-slate-500">Mavlink UDP (Active)</span></span>
      </div>
    </div>
  );
};
