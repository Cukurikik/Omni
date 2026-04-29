import React, { useState, useEffect } from 'react';

export const MatrioshkaTopology: React.FC = () => {
  const [computeLoad, setComputeLoad] = useState(10); // Yottaflops
  const [shell1Temp, setShell1Temp] = useState(300); // Inner (Hot)
  const [shell2Temp, setShell2Temp] = useState(100); // Middle
  const [shell3Temp, setShell3Temp] = useState(3);   // Outer (Cold)
  const [meltdown, setMeltdown] = useState(false);

  useEffect(() => {
    // Simulate Compute Load and Thermal Transfer
    const brain = setInterval(() => {
       if (!meltdown) {
          setComputeLoad(prev => {
             const next = prev + 50;
             return Math.min(1000, next); // Max 1000 Yottaflops
          });
          
          // Heat builds up in the inner shell based on compute load
          setShell1Temp(prev => {
             const next = prev + (computeLoad * 0.1);
             if (next > 4000) setMeltdown(true);
             return next;
          });
          
          // Heat transfers outward (Carnot engine simulation)
          setShell2Temp(prev => prev + (shell1Temp * 0.05) - (prev * 0.1));
          setShell3Temp(prev => prev + (shell2Temp * 0.02) - (prev * 0.05));
       }
    }, 200);

    return () => clearInterval(brain);
  }, [computeLoad, shell1Temp, shell2Temp, meltdown]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-pink-400">Matrioshka Brain</h2>
          <p className="text-xs text-slate-400">Planetary Megacomputer</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-bold border ${meltdown ? 'bg-red-900/80 text-white border-red-500 shadow-[0_0_15px_#ef4444] animate-pulse' : 'bg-slate-800 text-slate-400 border-slate-700'}`}>
          {meltdown ? 'THERMAL MELTDOWN' : 'SIMULATING REALITY'}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex items-center justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* The Star (Power Source) */}
         <div className="absolute w-8 h-8 rounded-full bg-white shadow-[0_0_40px_#fff]"></div>

         {/* Shell 1: Inner (Hot, high compute) */}
         <div 
            className={`absolute w-20 h-20 rounded-full border-4 ${meltdown ? 'border-red-500 shadow-[0_0_30px_#ef4444]' : 'border-yellow-500 shadow-[0_0_20px_#eab308]'} flex items-center justify-center animate-[spin_4s_linear_infinite]`}
            style={{ borderStyle: 'dashed' }}
         >
            <span className="absolute top-[-15px] text-[8px] text-yellow-400 bg-black/50 px-1 rounded">{shell1Temp.toFixed(0)}K</span>
         </div>

         {/* Shell 2: Middle */}
         <div 
            className={`absolute w-36 h-36 rounded-full border-4 border-orange-500 shadow-[0_0_15px_#f97316] flex items-center justify-center animate-[spin_8s_linear_infinite_reverse] ${meltdown ? 'opacity-50' : ''}`}
            style={{ borderStyle: 'dotted' }}
         >
            <span className="absolute top-[-15px] text-[8px] text-orange-400 bg-black/50 px-1 rounded">{shell2Temp.toFixed(0)}K</span>
         </div>

         {/* Shell 3: Outer (Cold, radiating to space) */}
         <div 
            className={`absolute w-52 h-52 rounded-full border-2 border-sky-500 shadow-[0_0_10px_#0ea5e9] flex items-center justify-center animate-[spin_16s_linear_infinite] ${meltdown ? 'opacity-20' : ''}`}
         >
            <span className="absolute top-[-15px] text-[8px] text-sky-400 bg-black/50 px-1 rounded">{shell3Temp.toFixed(1)}K</span>
         </div>

         {/* Data Streams (Simulation processing) */}
         {!meltdown && (
            <div className="absolute inset-0 flex justify-center items-center pointer-events-none opacity-40 mix-blend-screen">
               {[...Array(8)].map((_, i) => (
                  <div 
                     key={i} 
                     className="absolute w-full h-px bg-gradient-to-r from-transparent via-pink-400 to-transparent"
                     style={{ transform: `rotate(${i * 45}deg)` }}
                  ></div>
               ))}
            </div>
         )}
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Compute Capacity</div>
            <div className={`text-lg font-mono font-bold ${meltdown ? 'text-red-400' : 'text-pink-400'}`}>
               {meltdown ? '0.0' : computeLoad.toFixed(0)} <span className="text-xs text-slate-500">YFLOPS</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Carnot Efficiency</div>
            <div className="text-lg font-mono font-bold text-emerald-400">
               {meltdown ? '0.0' : ((1 - (shell3Temp / shell1Temp)) * 100).toFixed(1)} <span className="text-xs">%</span>
            </div>
         </div>
      </div>

      <div className="w-full bg-slate-950 rounded border border-slate-800 p-2 text-xs font-mono text-center">
         <span className={meltdown ? 'text-red-400 font-bold' : 'text-slate-400'}>
            {meltdown ? 'SUBSTRATE VAPORIZED - ANCESTORS DELETED' : 'REVERSIBLE LOGIC GATES STABLE'}
         </span>
      </div>
    </div>
  );
};
