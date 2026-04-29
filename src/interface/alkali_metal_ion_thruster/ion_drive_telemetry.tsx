import React, { useState, useEffect } from 'react';

export const IonDriveTelemetry: React.FC = () => {
  const [thrustMn, setThrustMn] = useState(250.0);
  const [velocityKmS, setVelocityKmS] = useState(15.2);
  const [gridVoltage, setGridVoltage] = useState(1400);
  const [plasmaColor, setPlasmaColor] = useState('cyan'); // Xenon is blue/cyan, Krypton is white/green

  useEffect(() => {
    // Simulate continuous ion burn
    const burn = setInterval(() => {
       // Thrust fluctuates slightly based on grid voltage anomalies
       setThrustMn(250.0 + (Math.random() - 0.5) * 5);
       
       // Velocity slowly accumulates (acceleration is tiny but constant)
       setVelocityKmS(prev => prev + 0.001);
       
       // Simulate minor voltage spikes
       if (Math.random() > 0.95) setGridVoltage(prev => prev + (Math.random() * 50));
       else setGridVoltage(prev => Math.max(1400, prev - 10));
       
    }, 100);

    return () => clearInterval(burn);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-cyan-400">Ion Thruster</h2>
          <p className="text-xs text-slate-400">Hall-Effect Drive</p>
        </div>
        <div className="px-2 py-1 rounded text-[10px] font-mono border bg-cyan-900/30 text-cyan-400 border-cyan-800 animate-pulse shadow-[0_0_10px_rgba(6,182,212,0.3)]">
          CONTINUOUS BURN
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex items-center justify-start shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* The Engine (Left Side) */}
         <div className="relative z-20 w-16 h-24 bg-slate-800 border-r-4 border-slate-600 rounded-r-3xl flex flex-col items-end justify-center py-2 shadow-[5px_0_15px_rgba(0,0,0,0.8)]">
            {/* Acceleration Grids */}
            <div className="w-2 h-16 bg-slate-500 rounded-r opacity-80 border-r border-white/30 flex flex-col justify-between py-1">
               {[...Array(6)].map((_, i) => (
                  <div key={i} className="w-full h-1 bg-black/50"></div>
               ))}
            </div>
         </div>

         {/* The Plasma Plume (Exhaust) */}
         <div className="relative z-10 h-16 flex-1 flex">
            {/* Core dense plasma */}
            <div className="h-full w-20 bg-gradient-to-r from-white via-cyan-400 to-transparent blur-sm rounded-r-full opacity-90 animate-[pulse_0.1s_linear_infinite]"></div>
            
            {/* Extended faint exhaust */}
            <div className="absolute inset-0 flex">
               <div className="h-full w-48 bg-gradient-to-r from-cyan-500/50 to-transparent blur-md rounded-r-full" style={{ transform: 'translateX(-10px)' }}></div>
            </div>
            
            {/* Accelerated Ion Particles */}
            <div className="absolute inset-0 overflow-hidden">
               {[...Array(30)].map((_, i) => (
                  <div 
                     key={i} 
                     className="absolute h-px w-4 bg-white shadow-[0_0_5px_#fff]"
                     style={{ 
                        top: `${Math.random() * 100}%`,
                        left: '0%',
                        animation: `shoot-right ${0.1 + Math.random() * 0.2}s linear infinite`
                     }}
                  ></div>
               ))}
            </div>
         </div>
         
         {/* Neutralizer Cathode Spark */}
         <div className="absolute z-30 w-1 h-1 bg-white rounded-full shadow-[0_0_10px_#fff] animate-ping" style={{ left: '60px', top: '35%' }}></div>
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Thrust</div>
            <div className="text-lg font-mono font-bold text-white">{thrustMn.toFixed(1)} <span className="text-xs text-slate-500">mN</span></div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Accumulated Velocity</div>
            <div className="text-lg font-mono font-bold text-emerald-400">
               {velocityKmS.toFixed(3)} <span className="text-xs text-slate-500">km/s</span>
            </div>
         </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded text-center">
         <span>Propellant: <span className="text-cyan-400">Xenon (Xe)</span></span>
         <span>Grid: <span className={gridVoltage > 1430 ? 'text-red-400 animate-pulse' : 'text-emerald-400'}>{Math.floor(gridVoltage)} V</span></span>
      </div>

      <style>{`
        @keyframes shoot-right {
          from { transform: translateX(0); opacity: 1; }
          to { transform: translateX(200px); opacity: 0; }
        }
      `}</style>
    </div>
  );
};
