import React, { useState, useEffect } from 'react';

export const MultiCloudMap: React.FC = () => {
  const [traffic, setTraffic] = useState({ aws: 45, gcp: 35, azure: 20 });

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate dynamic cloud arbitrage traffic shifting
      setTraffic(prev => {
         const shift = Math.random() > 0.5 ? 5 : -5;
         let newAws = Math.max(10, Math.min(80, prev.aws + shift));
         let newGcp = Math.max(10, Math.min(80, prev.gcp - (shift / 2)));
         let newAzure = 100 - newAws - newGcp;
         
         if (newAzure < 0) { newAzure = 0; newGcp = 100 - newAws; }
         
         return { aws: newAws, gcp: newGcp, azure: newAzure };
      });
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-sky-400">Cloud OS Router</h2>
          <p className="text-xs text-slate-400">Vendor-Agnostic Load Balancer</p>
        </div>
        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_#10b981]"></div>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 space-y-4 mb-4">
         
         {/* AWS Router */}
         <div>
            <div className="flex justify-between text-xs font-bold text-orange-400 mb-1">
               <span>AWS us-east-1</span>
               <span>{traffic.aws.toFixed(0)}% Traffic</span>
            </div>
            <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
               <div className="h-full bg-orange-500 transition-all duration-500" style={{ width: `${traffic.aws}%` }}></div>
            </div>
         </div>

         {/* GCP Router */}
         <div>
            <div className="flex justify-between text-xs font-bold text-blue-400 mb-1">
               <span>GCP us-central1</span>
               <span>{traffic.gcp.toFixed(0)}% Traffic</span>
            </div>
            <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
               <div className="h-full bg-blue-500 transition-all duration-500" style={{ width: `${traffic.gcp}%` }}></div>
            </div>
         </div>

         {/* Azure Router */}
         <div>
            <div className="flex justify-between text-xs font-bold text-sky-500 mb-1">
               <span>Azure eastus</span>
               <span>{traffic.azure.toFixed(0)}% Traffic</span>
            </div>
            <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
               <div className="h-full bg-sky-500 transition-all duration-500" style={{ width: `${traffic.azure}%` }}></div>
            </div>
         </div>

      </div>
      
      <div className="flex justify-between text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded border border-slate-700">
         <span>BGP eBPF Hook: <span className="text-emerald-400">Active</span></span>
         <span>Latency: 12ms</span>
         <span>Lock-in: <span className="text-emerald-400">0%</span></span>
      </div>
    </div>
  );
};
