import React, { useState, useEffect } from 'react';

export const TesseractStorage: React.FC = () => {
  const [dimensions, setDimensions] = useState(3);
  const [capacity, setCapacity] = useState(1); // Exabytes
  const [usage, setUsage] = useState(0); // %
  const [aligned, setAligned] = useState(true);

  useEffect(() => {
    // Capacity grows exponentially with dimension
    setCapacity(Math.pow(10, dimensions - 3));

    // Simulate usage filling up
    const writer = setInterval(() => {
       setUsage(prev => {
          const next = prev + (5 / dimensions); // Slower fill on higher dimensions
          if (next > 90 && Math.random() > 0.8) setAligned(false); // GC failure risk at high usage
          return next > 100 ? 0 : next; // Reset simulating GC
       });
    }, 200);

    return () => clearInterval(writer);
  }, [dimensions]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-pink-500">Hyper-Drive</h2>
          <p className="text-xs text-slate-400">Non-Euclidean Storage</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-bold border ${!aligned ? 'bg-red-900/80 text-white border-red-500 shadow-[0_0_15px_#ef4444] animate-pulse' : 'bg-slate-800 text-pink-400 border-slate-700'}`}>
          {!aligned ? 'W-AXIS MISALIGNED' : `${dimensions}D GEOMETRY`}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex flex-col justify-center items-center shadow-[inset_0_0_30px_rgba(0,0,0,1)] perspective-[800px]">
         
         {/* Tesseract Visualization (CSS approximation) */}
         <div 
            className={`relative w-24 h-24 transform-style-3d transition-transform duration-[3000ms] ${aligned ? 'animate-[spin_8s_linear_infinite]' : 'animate-[spin_1s_linear_infinite]'}`}
            style={{ transformStyle: 'preserve-3d', transform: 'rotateX(45deg) rotateZ(45deg)' }}
         >
            {/* Outer Cube */}
            <div className="absolute inset-0 border-2 border-pink-500/50 shadow-[0_0_15px_rgba(236,72,153,0.3)]"></div>
            
            {/* Inner Cube (representing 4th dimension offset) */}
            {dimensions >= 4 && (
               <div 
                  className="absolute inset-4 border-2 border-cyan-400/80 shadow-[0_0_10px_rgba(34,211,238,0.5)] transform-style-3d"
                  style={{ transform: 'translateZ(20px)' }}
               >
                  {/* Connectors (Tesseract edges) */}
                  <div className="absolute top-0 left-0 w-[140%] h-px bg-pink-400/50" style={{ transformOrigin: 'top left', transform: 'rotate(-45deg)' }}></div>
                  <div className="absolute top-0 right-0 w-[140%] h-px bg-pink-400/50" style={{ transformOrigin: 'top right', transform: 'rotate(45deg)' }}></div>
                  <div className="absolute bottom-0 left-0 w-[140%] h-px bg-pink-400/50" style={{ transformOrigin: 'bottom left', transform: 'rotate(45deg)' }}></div>
                  <div className="absolute bottom-0 right-0 w-[140%] h-px bg-pink-400/50" style={{ transformOrigin: 'bottom right', transform: 'rotate(-45deg)' }}></div>
               </div>
            )}

            {/* Penteract representation (5D) */}
            {dimensions === 5 && (
               <div 
                  className="absolute inset-8 border border-white/80 shadow-[0_0_20px_#fff] transform-style-3d animate-pulse"
                  style={{ transform: 'translateZ(-20px) rotate(45deg)' }}
               ></div>
            )}
         </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800 flex flex-col justify-between">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Spatial Dimensions</div>
            <div className="flex items-center gap-2">
               <button onClick={() => setDimensions(Math.max(3, dimensions - 1))} className="bg-slate-800 px-2 rounded hover:bg-slate-700">-</button>
               <span className="text-lg font-mono font-bold text-white">{dimensions}D</span>
               <button onClick={() => setDimensions(Math.min(5, dimensions + 1))} className="bg-slate-800 px-2 rounded hover:bg-slate-700">+</button>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800 flex flex-col justify-between">
            <div className="flex justify-between items-center mb-1">
               <span className="text-[10px] uppercase text-slate-500">Usage</span>
               <span className={`text-[10px] font-mono font-bold ${usage > 80 ? 'text-orange-400' : 'text-slate-300'}`}>{usage.toFixed(1)}%</span>
            </div>
            <div className="w-full bg-slate-800 h-2 rounded overflow-hidden">
               <div className={`h-full ${usage > 90 ? 'bg-red-500' : (usage > 70 ? 'bg-orange-500' : 'bg-pink-500')}`} style={{ width: `${usage}%` }}></div>
            </div>
            <div className="text-xs font-mono text-slate-400 mt-1">Cap: {capacity} <span className="text-[10px]">EB</span></div>
         </div>
      </div>

      <div className="w-full bg-slate-950 rounded border border-slate-800 p-2 text-[10px] font-mono flex justify-between items-center">
         <button 
            onClick={() => { setAligned(true); setUsage(0); }}
            className={`px-2 py-1 rounded border ${!aligned ? 'bg-emerald-900/50 text-emerald-400 border-emerald-500' : 'bg-slate-800 text-slate-500 border-slate-700'}`}
         >
            FORCE GC DEFRAG
         </button>
         <span className={!aligned ? 'text-red-400' : 'text-emerald-400'}>
            {!aligned ? 'DATA LEAKING INTO BULK' : 'ORTHOGONAL ALLOCATION STABLE'}
         </span>
      </div>
    </div>
  );
};
