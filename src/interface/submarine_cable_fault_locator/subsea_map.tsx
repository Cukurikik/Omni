import React, { useState, useEffect } from 'react';

export const SubseaMap: React.FC = () => {
  const [pulsePos, setPulsePos] = useState(0);
  const [faultDetected, setFaultDetected] = useState(false);
  const faultDistance = 65; // ~65% along the cable

  useEffect(() => {
    const interval = setInterval(() => {
      setPulsePos(prev => {
         const next = prev + 2;
         if (next >= faultDistance) {
            setFaultDetected(true);
            return faultDistance; // Stop at fault
         }
         return next;
      });
    }, 50);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-teal-400">Subsea Network</h2>
          <p className="text-xs text-slate-400">OTDR Fault Locator</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-mono border ${faultDetected ? 'bg-red-900/50 text-red-400 border-red-800 animate-pulse' : 'bg-teal-900/30 text-teal-400 border-teal-800'}`}>
          {faultDetected ? 'CABLE CUT' : 'PULSING LASER'}
        </div>
      </div>

      <div className="bg-[#0f172a] p-4 rounded border border-slate-800 mb-4 h-[120px] relative flex flex-col justify-center overflow-hidden">
         {/* Map Background (Mock Ocean) */}
         <div className="absolute inset-0 opacity-10 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-teal-500 via-blue-900 to-black"></div>

         <div className="flex justify-between text-[10px] font-mono text-slate-500 mb-2 z-10">
            <span>Tokyo, JP</span>
            <span>Los Angeles, US</span>
         </div>

         {/* The Cable */}
         <div className="w-full h-1 bg-slate-700 rounded relative z-10">
            {/* The Light Pulse */}
            {!faultDetected && (
               <div 
                  className="absolute top-1/2 transform -translate-y-1/2 w-4 h-2 bg-teal-400 rounded-full shadow-[0_0_10px_#2dd4bf]"
                  style={{ left: `${pulsePos}%` }}
               ></div>
            )}
            
            {/* The Fault */}
            {faultDetected && (
               <div 
                  className="absolute top-1/2 transform -translate-y-1/2 -translate-x-1/2 flex items-center justify-center"
                  style={{ left: `${faultDistance}%` }}
               >
                  <div className="w-4 h-4 bg-red-500 rounded-full animate-ping absolute"></div>
                  <div className="w-2 h-2 bg-white rounded-full relative"></div>
               </div>
            )}
         </div>
         
         <div className="flex justify-between text-[8px] font-mono text-slate-600 mt-2 z-10">
            <span>0 km</span>
            <span>8,800 km</span>
         </div>
      </div>
      
      {faultDetected && (
         <div className="bg-red-950/30 border border-red-900/50 p-3 rounded mb-4 text-xs font-mono text-red-300">
            <div className="font-bold text-red-400 mb-1">FAULT PINPOINTED:</div>
            <div>Distance: 5,720 km from origin</div>
            <div>Coords: 38°15'N 165°20'W (Abyssal Plain)</div>
            <div className="mt-2 text-emerald-400">Action: ROV Dispatch Initiated</div>
         </div>
      )}

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>EDFA Repeaters: <span className="text-white">Active</span></span>
         <span>DWDM Reroute: <span className="text-emerald-400">Success</span></span>
      </div>
    </div>
  );
};
