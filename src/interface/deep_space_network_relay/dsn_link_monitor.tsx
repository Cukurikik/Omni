import React, { useState, useEffect } from 'react';

export const DsnLinkMonitor: React.FC = () => {
  const [distanceKm, setDistanceKm] = useState(225000000); // ~Mars Distance
  const speedOfLight = 299792.458; // km/s

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate planetary orbits changing the distance slightly
      setDistanceKm(prev => prev + 100);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const owltSeconds = distanceKm / speedOfLight;
  const roundTripMinutes = (owltSeconds * 2) / 60;

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-orange-500">DSN Link</h2>
          <p className="text-xs text-slate-400">Earth-Mars Relay (ION DTN)</p>
        </div>
        <div className="px-2 py-1 bg-slate-800 text-orange-400 text-[10px] font-mono rounded border border-orange-900/50">
          DSS-14 Goldstone
        </div>
      </div>

      <div className="bg-slate-950 p-6 rounded border border-slate-800 flex flex-col items-center justify-center mb-4 relative">
         <div className="text-[10px] uppercase font-bold text-slate-500 mb-2">Round-Trip Light Time</div>
         <div className="text-4xl font-mono font-bold text-white drop-shadow-md">
            {roundTripMinutes.toFixed(1)} <span className="text-lg text-slate-400">mins</span>
         </div>
         <div className="text-[10px] font-mono text-slate-500 mt-2">
            Distance: {(distanceKm / 1000000).toFixed(2)} M km
         </div>
         
         {/* Signal Pulse Visualization */}
         <div className="absolute bottom-2 left-4 right-4 h-1 bg-slate-800 rounded overflow-hidden">
            <div className="w-4 h-full bg-orange-500 rounded animate-[slide_4s_linear_infinite]"></div>
         </div>
      </div>
      
      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Protocol: <span className="text-emerald-400">Bundle (DTN)</span></span>
         <span>Data Rate: <span className="text-white">2.0 Mbps</span></span>
         <span className="col-span-2">TCP/IP Status: <span className="text-red-400 font-bold">DISABLED (Timeout Risk)</span></span>
      </div>

      <style>{`
        @keyframes slide {
          0% { transform: translateX(0); }
          50% { transform: translateX(280px); }
          100% { transform: translateX(0); }
        }
      `}</style>
    </div>
  );
};
