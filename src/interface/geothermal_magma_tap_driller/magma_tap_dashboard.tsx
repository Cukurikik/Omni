import React, { useState, useEffect } from 'react';

export const MagmaTapDashboard: React.FC = () => {
  const [depthKm, setDepthKm] = useState(8.5);
  const [tempC, setTempC] = useState(700);
  const [pressureMpa, setPressureMpa] = useState(250);
  
  const targetDepth = 10.0; // km
  
  useEffect(() => {
    // Simulate drilling progress
    const drill = setInterval(() => {
      setDepthKm(prev => {
         const next = prev + 0.01;
         if (next >= targetDepth) return targetDepth;
         return next;
      });
      
      // Temperature and pressure increase with depth
      setTempC(prev => prev + 1.5 + Math.random() * 2);
      setPressureMpa(prev => prev + 0.5 + Math.random());
    }, 200);

    return () => clearInterval(drill);
  }, []);

  const isMagma = tempC > 900;

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-red-500">Magma Tap</h2>
          <p className="text-xs text-slate-400">Deep Geothermal Drilling</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-mono border ${isMagma ? 'bg-red-900/50 text-red-400 border-red-800 animate-pulse' : 'bg-amber-900/30 text-amber-400 border-amber-800'}`}>
          {isMagma ? 'CHAMBER BREACHED' : 'DRILLING'}
        </div>
      </div>

      <div className="flex gap-4 mb-4">
         {/* Borehole Visualizer (Vertical) */}
         <div className="w-16 h-[200px] bg-slate-950 rounded border border-slate-800 relative overflow-hidden flex justify-center">
            
            {/* Rock Layers */}
            <div className="absolute inset-0 bg-[linear-gradient(to_bottom,#475569_30%,#334155_60%,#1e1b4b_80%,#7f1d1d_100%)] opacity-50"></div>
            
            {/* The Drill String */}
            <div 
               className="w-2 bg-slate-400 absolute top-0 rounded-b transition-all duration-75 flex flex-col items-center shadow-md"
               style={{ height: `${(depthKm / targetDepth) * 100}%` }}
            >
               {/* Drill Bit */}
               <div className="absolute -bottom-2 w-4 h-3 bg-amber-500 clip-triangle animate-spin" style={{ animationDuration: '0.2s' }}></div>
            </div>

            <div className="absolute bottom-2 text-[8px] font-mono text-red-400">10 km</div>
         </div>
         
         <div className="flex-1 flex flex-col justify-between">
            <div className="bg-slate-950 p-3 rounded border border-slate-800">
               <div className="text-[10px] uppercase text-slate-500 mb-1">Depth</div>
               <div className="text-xl font-mono font-bold text-white">{depthKm.toFixed(2)} <span className="text-xs text-slate-400">km</span></div>
            </div>
            <div className="bg-slate-950 p-3 rounded border border-slate-800 relative overflow-hidden">
               <div className="text-[10px] uppercase text-slate-500 mb-1 relative z-10">Bottom Hole Temp</div>
               <div className={`text-xl font-mono font-bold relative z-10 ${isMagma ? 'text-red-400' : 'text-orange-400'}`}>
                  {tempC.toFixed(0)} <span className="text-xs">°C</span>
               </div>
               <div className={`absolute bottom-0 left-0 right-0 opacity-20 ${isMagma ? 'bg-red-500' : 'bg-orange-500'}`} style={{ height: `${(tempC / 1000) * 100}%` }}></div>
            </div>
            <div className="bg-slate-950 p-3 rounded border border-slate-800">
               <div className="text-[10px] uppercase text-slate-500 mb-1">Mud Pressure</div>
               <div className="text-xl font-mono font-bold text-sky-400">{pressureMpa.toFixed(0)} <span className="text-xs text-slate-400">MPa</span></div>
            </div>
         </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Telemetry: <span className="text-emerald-400">Acoustic 3 bps</span></span>
         <span>BOP Status: <span className="text-emerald-400">Overbalanced</span></span>
      </div>

      <style>{`
        .clip-triangle {
           clip-path: polygon(0 0, 100% 0, 50% 100%);
        }
      `}</style>
    </div>
  );
};
