import React, { useState, useEffect } from 'react';

export const QuantumFidelity: React.FC = () => {
  const [fidelity, setFidelity] = useState(0.999);
  const [blochVector, setBlochVector] = useState({ x: 0, y: 0, z: 1 }); // Starts at |0>
  const threshold = 0.990; // Surface code limit

  useEffect(() => {
    // Simulate coherence decay over time (microseconds)
    const decay = setInterval(() => {
      setFidelity(prev => {
         const next = prev - 0.001;
         if (next < 0.980) return 0.999; // Reset pulse applied
         return next;
      });

      // Wobble the Bloch vector as phase is lost
      setBlochVector(prev => ({
         x: prev.x + (Math.random() - 0.5) * 0.1,
         y: prev.y + (Math.random() - 0.5) * 0.1,
         z: Math.max(-1, Math.min(1, prev.z - 0.05)) // Slowly collapsing towards equator
      }));
    }, 200);

    return () => clearInterval(decay);
  }, []);

  const isViable = fidelity >= threshold;

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-fuchsia-400">Quantum Bus</h2>
          <p className="text-xs text-slate-400">Transmon Qubit Coherence</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-mono border ${isViable ? 'bg-fuchsia-900/30 text-fuchsia-400 border-fuchsia-800' : 'bg-red-900/50 text-red-400 border-red-800 animate-pulse'}`}>
          {isViable ? 'SURFACE CODE OK' : 'DECOHERENCE'}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[180px] flex items-center justify-center relative overflow-hidden">
         
         {/* Bloch Sphere Visualizer */}
         <div className="w-32 h-32 rounded-full border border-slate-600 relative flex items-center justify-center shadow-[inset_0_0_20px_rgba(255,255,255,0.1)]">
            {/* Equator */}
            <div className="w-full h-8 border border-slate-700 rounded-[50%] absolute transform -rotate-12"></div>
            
            {/* Z-Axis (|0> and |1>) */}
            <div className="w-px h-full bg-slate-600 absolute"></div>
            <div className="absolute -top-4 text-[10px] font-mono text-slate-400">|0⟩</div>
            <div className="absolute -bottom-4 text-[10px] font-mono text-slate-400">|1⟩</div>

            {/* The State Vector (Red Arrow) */}
            <div 
               className="w-px bg-fuchsia-500 absolute origin-bottom transition-all duration-75"
               style={{ 
                  height: '50%',
                  top: '0',
                  transform: `rotateX(${blochVector.y * 90}deg) rotateZ(${blochVector.x * 45}deg) rotateY(${blochVector.z * 10}deg)`,
                  boxShadow: '0 0 5px #d946ef'
               }}
            >
               {/* Arrow head */}
               <div className="w-2 h-2 bg-fuchsia-400 rounded-full absolute -top-1 -left-[3px] shadow-[0_0_8px_#d946ef]"></div>
            </div>
         </div>
      </div>
      
      <div className="space-y-2 mb-4">
         <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400">State Fidelity (F)</span>
            <span className={`font-bold font-mono ${isViable ? 'text-emerald-400' : 'text-red-400'}`}>
               {(fidelity * 100).toFixed(2)}%
            </span>
         </div>
         {/* Fidelity Bar */}
         <div className="w-full h-1 bg-slate-800 rounded relative">
            <div className={`absolute top-0 bottom-0 left-0 transition-all ${isViable ? 'bg-emerald-500' : 'bg-red-500'}`} style={{ width: `${fidelity * 100}%` }}></div>
            <div className="absolute top-0 bottom-0 w-px bg-white z-10" style={{ left: `${threshold * 100}%` }}></div>
         </div>
         <div className="text-[8px] text-slate-500 font-mono text-right">QEC Threshold: {threshold * 100}%</div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>T1 Decay: <span className="text-white">45.2 μs</span></span>
         <span>T2 Dephase: <span className="text-white">32.8 μs</span></span>
      </div>
    </div>
  );
};
