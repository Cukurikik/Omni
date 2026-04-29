import React, { useState, useEffect } from 'react';

export const SensorOverlay: React.FC = () => {
  const [gps, setGps] = useState(50);
  const [imu, setImu] = useState(50);
  const [fused, setFused] = useState(50);

  useEffect(() => {
    let t = 0;
    const interval = setInterval(() => {
      t += 0.1;
      // GPS is accurate but slow/noisy (low frequency)
      const gpsNoise = Math.sin(t) * 10 + (Math.random() * 20 - 10);
      
      // IMU is fast but drifts over time
      const imuDrift = Math.cos(t) * 5 + (t * 2);
      
      // Fused is the Kalman filtered optimal estimate
      const optimal = Math.sin(t) * 10;

      setGps(50 + gpsNoise);
      setImu(50 + imuDrift);
      setFused(50 + optimal);
    }, 100);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-emerald-400">Sensor Fusion</h2>
          <p className="text-xs text-slate-400">Kalman Filter State</p>
        </div>
        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 h-[160px] relative overflow-hidden mb-4">
         {/* Center Line */}
         <div className="absolute top-0 bottom-0 left-[50%] w-px bg-slate-700 border-l border-dashed border-slate-600"></div>

         {/* GPS Node (Noisy) */}
         <div 
           className="absolute w-3 h-3 bg-rose-500/50 rounded-full border border-rose-500 transform -translate-x-1/2 -translate-y-1/2 transition-all duration-100"
           style={{ top: '30%', left: `${Math.max(5, Math.min(95, gps))}%` }}
         ></div>

         {/* IMU Node (Drifting) */}
         <div 
           className="absolute w-3 h-3 bg-sky-500/50 rounded-full border border-sky-500 transform -translate-x-1/2 -translate-y-1/2 transition-all duration-100"
           style={{ top: '60%', left: `${Math.max(5, Math.min(95, imu))}%` }}
         ></div>

         {/* Fused Node (Clean) */}
         <div 
           className="absolute w-5 h-5 bg-emerald-500 rounded-full shadow-[0_0_15px_#10b981] transform -translate-x-1/2 -translate-y-1/2 transition-all duration-100 flex items-center justify-center"
           style={{ top: '45%', left: `${Math.max(5, Math.min(95, fused))}%` }}
         >
            <div className="w-1 h-1 bg-white rounded-full"></div>
         </div>
      </div>
      
      <div className="flex justify-between text-[10px] font-mono">
         <div className="flex items-center gap-1"><div className="w-2 h-2 bg-rose-500 rounded-full"></div> GPS (Noisy)</div>
         <div className="flex items-center gap-1"><div className="w-2 h-2 bg-emerald-500 rounded-full"></div> Fused (Clean)</div>
         <div className="flex items-center gap-1"><div className="w-2 h-2 bg-sky-500 rounded-full"></div> IMU (Drift)</div>
      </div>
    </div>
  );
};
