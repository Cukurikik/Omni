import React, { useState, useEffect } from 'react';

export const InferenceDash: React.FC = () => {
  const [fps, setFps] = useState(0);
  const [power, setPower] = useState(0);
  const [isQuantized, setIsQuantized] = useState(false);

  useEffect(() => {
    // Toggle between FP32 (Slow/High Power) and INT8 (Fast/Low Power)
    const toggle = setInterval(() => {
       setIsQuantized(prev => !prev);
    }, 5000);

    const metrics = setInterval(() => {
       setFps(isQuantized ? 120 + Math.random() * 5 : 24 + Math.random() * 2);
       setPower(isQuantized ? 2.1 + Math.random() * 0.2 : 8.5 + Math.random() * 0.5);
    }, 500);

    return () => { clearInterval(toggle); clearInterval(metrics); };
  }, [isQuantized]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-lime-400">Edge AI NPU</h2>
          <p className="text-xs text-slate-400">Object Detection (YOLOv8)</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-mono border transition-colors ${isQuantized ? 'bg-lime-900/30 text-lime-400 border-lime-800' : 'bg-sky-900/30 text-sky-400 border-sky-800'}`}>
          {isQuantized ? 'INT8 PTQ' : 'FP32 FLOAT'}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-4 rounded border border-slate-800 text-center">
            <div className="text-[10px] uppercase font-bold text-slate-500 mb-1">Inference Speed</div>
            <div className={`text-3xl font-mono font-bold transition-colors ${isQuantized ? 'text-lime-400' : 'text-sky-400'}`}>
               {fps.toFixed(0)} <span className="text-sm">FPS</span>
            </div>
         </div>
         
         <div className="bg-slate-950 p-4 rounded border border-slate-800 text-center relative overflow-hidden">
            <div className="text-[10px] uppercase font-bold text-slate-500 mb-1 z-10 relative">Power Draw</div>
            <div className={`text-3xl font-mono font-bold z-10 relative transition-colors ${isQuantized ? 'text-emerald-400' : 'text-red-400'}`}>
               {power.toFixed(1)} <span className="text-sm">W</span>
            </div>
            {/* Battery Drain Background */}
            <div 
               className={`absolute bottom-0 left-0 right-0 opacity-20 transition-all duration-500 ${isQuantized ? 'bg-emerald-500' : 'bg-red-500'}`}
               style={{ height: `${(power / 10) * 100}%` }}
            ></div>
         </div>
      </div>
      
      <div className="space-y-2 mb-4">
         <div className="text-xs font-mono text-slate-400">Memory Footprint:</div>
         <div className="w-full h-4 bg-slate-800 rounded overflow-hidden flex">
            {/* Green is INT8 memory, Red is the extra memory used by FP32 */}
            <div className="h-full bg-lime-500 transition-all duration-500" style={{ width: isQuantized ? '25%' : '25%' }}></div>
            <div className="h-full bg-slate-600 transition-all duration-500" style={{ width: isQuantized ? '0%' : '75%' }}></div>
         </div>
         <div className="flex justify-between text-[10px] font-mono text-slate-500">
            <span>{isQuantized ? '42 MB' : '168 MB'}</span>
         </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Accuracy mAP: <span className={isQuantized ? 'text-amber-400' : 'text-emerald-400'}>{isQuantized ? '81.2%' : '82.5%'}</span></span>
         <span>Hardware: <span className="text-white">Edge TPU</span></span>
      </div>
    </div>
  );
};
