import React, { useState, useEffect } from 'react';

export const ThermalMap: React.FC = () => {
  const [zones, setZones] = useState([22.5, 23.1, 21.8, 24.0, 22.2, 23.5]); // Initial temps
  const [savings, setSavings] = useState(0);

  useEffect(() => {
    // Simulate MPC AI optimizing temperatures towards a baseline (22.5) while saving energy
    const interval = setInterval(() => {
      setZones(prev => prev.map(t => {
         // Slowly pull towards 22.5
         const diff = 22.5 - t;
         return t + (diff * 0.1) + (Math.random() - 0.5) * 0.2;
      }));
      setSavings(prev => prev + 0.1); // Accumulate saved kW
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  // Helper to colorize based on temp (Blue < 22 < Green < 23 < Red)
  const getTempColor = (t: number) => {
     if (t < 22.0) return 'bg-sky-500';
     if (t > 23.5) return 'bg-orange-500';
     return 'bg-emerald-500'; // Comfort sweet spot
  };

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-sky-400">Smart Building</h2>
          <p className="text-xs text-slate-400">MPC HVAC Optimizer</p>
        </div>
        <div className="text-[10px] font-mono bg-emerald-900/30 text-emerald-400 border border-emerald-800 px-2 py-1 rounded">
          ASHRAE COMPLIANT
        </div>
      </div>

      {/* Building Floorplan Map */}
      <div className="bg-[#0f172a] p-4 rounded border border-slate-800 mb-4 grid grid-cols-3 grid-rows-2 gap-2 h-[160px]">
         {zones.map((temp, i) => (
            <div key={i} className="bg-slate-950 border border-slate-800 rounded relative overflow-hidden flex flex-col items-center justify-center">
               <span className="text-[10px] text-slate-500 absolute top-1 left-1">Z{i+1}</span>
               <span className="text-lg font-mono font-bold text-white z-10">{temp.toFixed(1)}°</span>
               
               {/* Thermal Background Glow */}
               <div className={`absolute bottom-0 left-0 right-0 h-2/3 opacity-30 ${getTempColor(temp)} filter blur-xl`}></div>
            </div>
         ))}
      </div>
      
      <div className="space-y-2 mb-4">
         <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400">Energy Savings (Cumulative)</span>
            <span className="font-bold font-mono text-emerald-400">{savings.toFixed(1)} kWh</span>
         </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Sensors: <span className="text-white">Fused</span></span>
         <span>Protocol: <span className="text-sky-400">BACnet UDP</span></span>
      </div>
    </div>
  );
};
