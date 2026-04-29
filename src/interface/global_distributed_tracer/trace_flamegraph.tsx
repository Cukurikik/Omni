import React, { useState, useEffect } from 'react';

export const TraceFlamegraph: React.FC = () => {
  const [requestCount, setRequestCount] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setRequestCount(r => r + 1);
    }, 1200); // New distributed trace every 1.2s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-indigo-400">Distributed Trace</h2>
          <p className="text-xs text-slate-400">Multi-Cloud DAG Path</p>
        </div>
        <div className="text-[10px] font-mono bg-indigo-900/30 text-indigo-400 border border-indigo-800 px-2 py-1 rounded">
          Req #{requestCount}
        </div>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 relative h-[180px] mb-4 overflow-hidden">
         {/* Flame Graph / Waterfall Visualization */}
         <div className="space-y-1 relative w-full h-full flex flex-col justify-start pt-2">
            
            {/* API Gateway (AWS) */}
            <div className="flex items-center group cursor-crosshair">
               <div className="w-[100%] h-4 bg-orange-500 rounded-sm shadow-[0_0_5px_#f97316] opacity-90 group-hover:opacity-100 flex items-center px-1 text-[8px] font-mono font-bold text-white overflow-hidden whitespace-nowrap">
                  aws-api-gateway (240ms)
               </div>
            </div>

            {/* Auth Service (GCP) */}
            <div className="flex items-center pl-4 group cursor-crosshair">
               <div className="w-[30%] h-4 bg-blue-500 rounded-sm shadow-[0_0_5px_#3b82f6] opacity-90 group-hover:opacity-100 flex items-center px-1 text-[8px] font-mono font-bold text-white overflow-hidden whitespace-nowrap">
                  gcp-auth (60ms)
               </div>
            </div>

            {/* Payment Processor (Azure) - Parallel */}
            <div className="flex items-center pl-4 group cursor-crosshair">
               <div className="w-[60%] ml-[30%] h-4 bg-sky-500 rounded-sm shadow-[0_0_5px_#0ea5e9] opacity-90 group-hover:opacity-100 flex items-center px-1 text-[8px] font-mono font-bold text-white overflow-hidden whitespace-nowrap">
                  azure-payment (150ms)
               </div>
            </div>

            {/* DB Query (AWS Aurora) */}
            <div className="flex items-center pl-8 group cursor-crosshair">
               <div className="w-[40%] ml-[30%] h-4 bg-orange-400 rounded-sm shadow-[0_0_5px_#fb923c] opacity-90 group-hover:opacity-100 flex items-center px-1 text-[8px] font-mono font-bold text-white overflow-hidden whitespace-nowrap">
                  aws-aurora-db (110ms)
               </div>
            </div>

            {/* Redis Cache (GCP) */}
            <div className="flex items-center pl-12 group cursor-crosshair">
               <div className="w-[15%] ml-[30%] h-4 bg-blue-400 rounded-sm shadow-[0_0_5px_#60a5fa] opacity-90 group-hover:opacity-100 flex items-center px-1 text-[8px] font-mono font-bold text-white overflow-hidden whitespace-nowrap">
                  redis (25ms)
               </div>
            </div>
            
            {/* Playhead Scanner Line */}
            <div className="absolute top-0 bottom-0 w-px bg-white/20 animate-[scan_1.2s_ease-in-out_infinite]" style={{ left: '0%' }}></div>
         </div>
      </div>
      
      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Total Latency: <span className="text-white">240ms</span></span>
         <span>Critical Path: <span className="text-orange-400">aws-api-gateway</span></span>
         <span className="col-span-2">Trace ID: 7a8f9c0b1e2d3c4a</span>
      </div>

      <style>{`
        @keyframes scan {
          0% { left: 0%; opacity: 1; }
          90% { left: 100%; opacity: 1; }
          100% { left: 100%; opacity: 0; }
        }
      `}</style>
    </div>
  );
};
