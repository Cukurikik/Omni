import React, { useState, useEffect } from 'react';

export const RdmaThroughput: React.FC = () => {
  const [throughput, setThroughput] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate 400 Gbps Infiniband NDR connection with slight variations
      setThroughput(380 + Math.random() * 15);
    }, 200);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-sky-400">RDMA Bridge</h2>
          <p className="text-xs text-slate-400">GPU-Direct Infiniband</p>
        </div>
        <div className="w-2 h-2 rounded-full bg-sky-500 animate-pulse shadow-[0_0_8px_#0ea5e9]"></div>
      </div>

      <div className="bg-slate-950 p-6 rounded border border-slate-800 text-center mb-4 relative overflow-hidden">
         <div className="text-[10px] uppercase font-bold text-slate-500 mb-2">Network Throughput</div>
         <div className="text-5xl font-mono text-sky-400 font-bold drop-shadow-[0_0_10px_rgba(14,165,233,0.5)]">
            {throughput.toFixed(1)}
         </div>
         <div className="text-xs text-sky-500 mt-1 font-mono">Gbps (NDR 400G)</div>
         
         {/* Simulated data laser beam */}
         <div className="absolute bottom-0 left-0 h-1 bg-sky-500 w-full animate-pulse"></div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono">
         <div className="bg-slate-800 p-2 rounded border border-slate-700">
            <span className="text-slate-500 block">Kernel Bypass</span>
            <span className="text-emerald-400 font-bold">ACTIVE</span>
         </div>
         <div className="bg-slate-800 p-2 rounded border border-slate-700">
            <span className="text-slate-500 block">NUMA Alignment</span>
            <span className="text-emerald-400 font-bold">Node 0</span>
         </div>
         <div className="bg-slate-800 p-2 rounded border border-slate-700 col-span-2">
            <span className="text-slate-500 block">Latency (Host to Host)</span>
            <span className="text-white">1.2 Microseconds</span>
         </div>
      </div>
    </div>
  );
};
