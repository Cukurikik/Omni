import React, { useState, useEffect } from 'react';

export const EmbeddedStorage: React.FC = () => {
  const [indexedMb, setIndexedMb] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setIndexedMb(prev => {
        if (prev >= 45.5) {
          clearInterval(interval);
          return 45.5;
        }
        return prev + 2.5;
      });
    }, 400);
    return () => clearInterval(interval);
  }, []);

  const totalCapacity = 128; // MB

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-pink-400">Embedded RAG</h2>
          <p className="text-xs text-slate-400">IoT Local Vector DB</p>
        </div>
        <div className="text-xl">📱</div>
      </div>

      <div className="mb-2 flex justify-between text-xs font-mono text-slate-400">
         <span>Storage Allocation</span>
         <span>{indexedMb.toFixed(1)} / {totalCapacity} MB</span>
      </div>

      <div className="w-full h-8 bg-slate-950 rounded border border-slate-800 overflow-hidden flex relative mb-4">
         {/* System Partition */}
         <div className="h-full bg-slate-600 flex items-center justify-center border-r border-slate-800" style={{ width: '20%' }}>
            <span className="text-[8px] uppercase font-bold">OS</span>
         </div>
         
         {/* App Partition */}
         <div className="h-full bg-slate-500 flex items-center justify-center border-r border-slate-800" style={{ width: '15%' }}>
            <span className="text-[8px] uppercase font-bold">App</span>
         </div>
         
         {/* Vector DB Partition */}
         <div 
           className="h-full bg-pink-500 flex items-center justify-center transition-all duration-300 relative overflow-hidden" 
           style={{ width: `${(indexedMb / totalCapacity) * 100}%` }}
         >
            {indexedMb < 45.5 && <div className="absolute inset-0 bg-white/20 animate-pulse"></div>}
            <span className="text-[8px] uppercase font-bold">V-DB</span>
         </div>
      </div>

      <div className="bg-slate-950 p-3 rounded border border-slate-800 text-xs font-mono space-y-1 text-slate-400">
         <div className="flex justify-between">
            <span>Quantization:</span>
            <span className="text-pink-400">PQ (8-bit)</span>
         </div>
         <div className="flex justify-between">
            <span>Vectors Indexed:</span>
            <span className="text-white">{(indexedMb * 1250).toFixed(0)}</span>
         </div>
         <div className="flex justify-between">
            <span>Flash Wear (TBW):</span>
            <span className="text-emerald-400">0.01%</span>
         </div>
      </div>
    </div>
  );
};
