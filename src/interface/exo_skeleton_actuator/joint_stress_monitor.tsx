import React, { useState, useEffect } from 'react';

export const JointStressMonitor: React.FC = () => {
  const [emg, setEmg] = useState(15);
  const [torque, setTorque] = useState(10);
  const maxTorque = 120; // Human limit in Nm

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate human muscle flexion (EMG) and the resulting Exoskeleton torque assist
      setEmg(prev => {
         // Random walk with occasional spikes
         const next = prev + (Math.random() * 20 - 10);
         const clamped = Math.max(5, Math.min(80, next));
         
         // Torque follows EMG after filtering
         setTorque(clamped * 1.5 + (Math.random()*5));
         return clamped;
      });
    }, 100);
    return () => clearInterval(interval);
  }, []);

  const torquePercent = (torque / maxTorque) * 100;
  const isDanger = torque > maxTorque * 0.85;

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-amber-400">Exo-Actuator</h2>
          <p className="text-xs text-slate-400">Knee Joint Force Feedback</p>
        </div>
        <div className={`text-[10px] font-mono px-2 py-1 rounded border ${isDanger ? 'bg-red-900/50 text-red-400 border-red-800 animate-pulse' : 'bg-emerald-900/30 text-emerald-400 border-emerald-800'}`}>
          {isDanger ? 'TORQUE WARN' : 'SAFE MARGIN'}
        </div>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 mb-4 flex flex-col space-y-4">
         
         {/* Raw EMG Signal */}
         <div>
            <div className="flex justify-between text-[10px] uppercase font-bold text-slate-500 mb-1">
               <span>Raw Muscle EMG (mV)</span>
               <span className="text-amber-400">{emg.toFixed(1)} mV</span>
            </div>
            <div className="w-full h-8 flex items-center overflow-hidden border-b border-slate-800">
               {/* Simulating a noisy signal wave */}
               <svg width="100%" height="100%" preserveAspectRatio="none">
                  <path 
                     d={`M 0,16 Q 10,${emg/2} 20,16 T 40,16 T 60,${32-emg/2} T 80,16 T 100,16 T 120,${emg/3} T 140,16 T 160,16 T 180,${32-emg/3} T 200,16`} 
                     fill="none" stroke="#fbbf24" strokeWidth="2"
                     className="animate-[pulse_0.5s_linear_infinite]"
                  />
               </svg>
            </div>
         </div>

         {/* Hydraulic Torque Output */}
         <div>
            <div className="flex justify-between text-[10px] uppercase font-bold text-slate-500 mb-1">
               <span>Servo Torque Assist (Nm)</span>
               <span className={isDanger ? 'text-red-400 font-bold' : 'text-sky-400'}>{torque.toFixed(1)} / {maxTorque} Nm</span>
            </div>
            <div className="w-full h-3 bg-slate-800 rounded-full overflow-hidden relative">
               <div 
                 className={`absolute top-0 bottom-0 left-0 transition-all duration-100 ${isDanger ? 'bg-red-500' : 'bg-sky-500'}`}
                 style={{ width: `${Math.min(100, torquePercent)}%` }}
               ></div>
               <div className="absolute top-0 bottom-0 w-0.5 bg-rose-500 z-10" style={{ left: '85%' }}></div>
            </div>
         </div>
      </div>
      
      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>PID Loop: <span className="text-white">1000 Hz</span></span>
         <span>CAN-Bus: <span className="text-emerald-400">Active</span></span>
      </div>
    </div>
  );
};
