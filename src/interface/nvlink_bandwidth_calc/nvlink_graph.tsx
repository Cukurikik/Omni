import React, { useState, useEffect } from 'react';

export const NvlinkGraph: React.FC = () => {
  const [activeNode, setActiveNode] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate AllReduce operations cycling through GPUs
      setActiveNode(prev => (prev + 1) % 8);
    }, 500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-emerald-500">NVSwitch</h2>
          <p className="text-xs text-slate-400">HGX 8-GPU Interconnect</p>
        </div>
        <div className="px-2 py-1 bg-emerald-900/30 text-emerald-500 text-[10px] font-mono rounded border border-emerald-800">
          900 GB/s
        </div>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 h-[200px] relative flex flex-col items-center justify-between mb-4">
         
         {/* Top Row GPUs (0-3) */}
         <div className="flex w-full justify-around z-10">
            {[0,1,2,3].map(i => (
               <div key={i} className={`w-8 h-10 border rounded transition-all duration-300 flex items-center justify-center text-[10px] font-mono ${activeNode === i ? 'bg-emerald-500 border-emerald-300 shadow-[0_0_10px_#10b981]' : 'bg-slate-800 border-slate-600'}`}>
                  G{i}
               </div>
            ))}
         </div>
         
         {/* NVSwitch Core */}
         <div className="w-3/4 h-12 bg-slate-800 border border-slate-600 rounded flex items-center justify-center z-20 relative">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">NVSwitch Matrix</span>
            
            {/* Simulated Data Beams */}
            <div className="absolute inset-x-0 top-0 h-0.5 bg-emerald-500/50 animate-pulse"></div>
            <div className="absolute inset-x-0 bottom-0 h-0.5 bg-emerald-500/50 animate-pulse"></div>
         </div>

         {/* Bottom Row GPUs (4-7) */}
         <div className="flex w-full justify-around z-10">
            {[4,5,6,7].map(i => (
               <div key={i} className={`w-8 h-10 border rounded transition-all duration-300 flex items-center justify-center text-[10px] font-mono ${activeNode === i ? 'bg-emerald-500 border-emerald-300 shadow-[0_0_10px_#10b981]' : 'bg-slate-800 border-slate-600'}`}>
                  G{i}
               </div>
            ))}
         </div>

         {/* Abstract background links connecting everything */}
         <svg className="absolute inset-0 w-full h-full pointer-events-none z-0 opacity-20">
            <path d="M 40,40 L 160,100 M 120,40 L 160,100 M 200,40 L 160,100 M 280,40 L 160,100" stroke="#10b981" strokeWidth="2" />
            <path d="M 40,160 L 160,100 M 120,160 L 160,100 M 200,160 L 160,100 M 280,160 L 160,100" stroke="#10b981" strokeWidth="2" />
         </svg>
      </div>
      
      <div className="text-center text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         Executing <span className="text-white">NCCL AllReduce</span> via GPU-Direct P2P
      </div>
    </div>
  );
};
