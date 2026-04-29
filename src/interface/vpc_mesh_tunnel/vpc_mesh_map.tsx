import React, { useState, useEffect } from 'react';

export const VpcMeshMap: React.FC = () => {
  const [activeTunnels, setActiveTunnels] = useState<number[]>([]);

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate traffic pulsing across the VPC Mesh (Zero-Trust tunnels)
      const t1 = Math.random() > 0.3 ? 1 : null;
      const t2 = Math.random() > 0.5 ? 2 : null;
      const t3 = Math.random() > 0.7 ? 3 : null;
      
      setActiveTunnels([t1, t2, t3].filter(x => x !== null) as number[]);
    }, 800);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-fuchsia-400">VPC Mesh</h2>
          <p className="text-xs text-slate-400">Zero-Trust WireGuard Tunnels</p>
        </div>
        <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_#10b981]"></div>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 relative h-[200px] mb-4 flex items-center justify-center">
         
         {/* AWS VPC */}
         <div className="absolute top-4 left-4 flex flex-col items-center">
            <div className="w-12 h-12 bg-orange-900/40 border border-orange-500 rounded flex items-center justify-center shadow-[0_0_15px_rgba(249,115,22,0.2)] z-10">
               <span className="text-xs font-bold text-orange-400">AWS</span>
            </div>
         </div>

         {/* GCP VPC */}
         <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex flex-col items-center">
            <div className="w-12 h-12 bg-blue-900/40 border border-blue-500 rounded flex items-center justify-center shadow-[0_0_15px_rgba(59,130,246,0.2)] z-10">
               <span className="text-xs font-bold text-blue-400">GCP</span>
            </div>
         </div>

         {/* Azure VPC */}
         <div className="absolute top-4 right-4 flex flex-col items-center">
            <div className="w-12 h-12 bg-sky-900/40 border border-sky-500 rounded flex items-center justify-center shadow-[0_0_15px_rgba(14,165,233,0.2)] z-10">
               <span className="text-xs font-bold text-sky-400">AZR</span>
            </div>
         </div>

         {/* Tunnels (SVG) */}
         <svg className="absolute inset-0 w-full h-full pointer-events-none z-0">
            {/* AWS to Azure */}
            <path 
               d="M 64,40 L 256,40" 
               stroke={activeTunnels.includes(1) ? "#e879f9" : "#334155"} 
               strokeWidth="3" strokeDasharray="5 5" 
               className={activeTunnels.includes(1) ? "animate-[dash_1s_linear_infinite]" : ""}
            />
            {/* AWS to GCP */}
            <path 
               d="M 50,64 L 140,160" 
               stroke={activeTunnels.includes(2) ? "#e879f9" : "#334155"} 
               strokeWidth="3" strokeDasharray="5 5"
               className={activeTunnels.includes(2) ? "animate-[dash_1s_linear_infinite]" : ""}
            />
            {/* Azure to GCP */}
            <path 
               d="M 270,64 L 180,160" 
               stroke={activeTunnels.includes(3) ? "#e879f9" : "#334155"} 
               strokeWidth="3" strokeDasharray="5 5"
               className={activeTunnels.includes(3) ? "animate-[dash_1s_linear_infinite]" : ""}
            />
         </svg>
      </div>
      
      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Encryption: <span className="text-white">ChaCha20</span></span>
         <span>Key Rotation: <span className="text-emerald-400">2h 45m</span></span>
         <span className="col-span-2">Policy: <span className="text-rose-400 font-bold">DEFAULT DENY (Zero-Trust)</span></span>
      </div>

      <style>{`
        @keyframes dash { to { stroke-dashoffset: -10; } }
      `}</style>
    </div>
  );
};
