import React, { useState, useEffect } from 'react';

export const AllocationGraph: React.FC = () => {
  const [heapData, setHeapData] = useState<number[]>([120, 125, 132, 128, 145, 150, 162]);
  const [alert, setAlert] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setHeapData(prev => {
        const nextVal = prev[prev.length - 1] + (Math.random() * 15 + 2); // Upward trend
        const next = [...prev.slice(1), nextVal];
        
        if (nextVal > 250) {
           setAlert(true);
           clearInterval(interval);
        }
        return next;
      });
    }, 800);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-yellow-400">Leak Detector</h2>
          <p className="text-xs text-slate-400">eBPF Heap Tracking</p>
        </div>
        <div className={`text-xs px-2 py-1 rounded font-bold uppercase transition-colors ${alert ? 'bg-red-900 text-red-200' : 'bg-emerald-900 text-emerald-200'}`}>
           {alert ? 'OOM Risk' : 'Stable'}
        </div>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 h-[150px] relative flex items-end gap-1 overflow-hidden">
         
         {/* Critical Threshold Line */}
         <div className="absolute top-[20%] left-0 right-0 h-px bg-red-500/50 border-b border-dashed border-red-500 z-0">
            <span className="absolute -top-3 right-1 text-[8px] text-red-400 font-mono">250MB Limit</span>
         </div>

         {/* Histogram Bars */}
         {heapData.map((val, i) => (
           <div key={i} className="flex-1 flex flex-col justify-end items-center h-full relative z-10">
              <div 
                className={`w-full rounded-t transition-all duration-300 ${val > 250 ? 'bg-red-500 shadow-[0_0_10px_#ef4444]' : 'bg-yellow-500'}`}
                style={{ height: `${Math.min(100, (val / 300) * 100)}%` }}
              ></div>
           </div>
         ))}
      </div>
      
      {alert && (
         <div className="mt-4 p-3 bg-slate-800 rounded border border-red-900 shadow-inner animate-fade-in">
            <div className="text-xs text-red-400 font-mono flex items-start gap-2">
               <span className="mt-0.5">⚠️</span> 
               <span>Trend analysis detects a memory leak in <span className="bg-slate-900 px-1 rounded text-white">cache_invalidator()</span>. Projected OOM in 14 minutes.</span>
            </div>
         </div>
      )}
    </div>
  );
};
