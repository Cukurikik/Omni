import React, { useState, useEffect } from 'react';

export const HolographicProjection: React.FC = () => {
  const [dataDensity, setDataDensity] = useState(10); // % of Bekenstein limit
  const [collapseAlert, setCollapseAlert] = useState(false);
  const [rendering, setRendering] = useState(true);

  useEffect(() => {
    // Simulate Universe Rendering
    const sim = setInterval(() => {
       if (rendering) {
          setDataDensity(prev => {
             // Slowly fill up the space with complex data (entropy)
             const next = prev + (Math.random() * 2);
             if (next > 100) {
                setCollapseAlert(true);
                return 100;
             }
             return next;
          });
       } else {
          // Garbage collection / black hole evaporation
          setDataDensity(prev => {
             const next = prev - 5;
             if (next < 90) setCollapseAlert(false);
             return Math.max(0, next);
          });
       }
    }, 200);

    return () => clearInterval(sim);
  }, [rendering]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-teal-400">Holographic Matrix</h2>
          <p className="text-xs text-slate-400">Bulk-Boundary Projection</p>
        </div>
        <button 
           onClick={() => setRendering(!rendering)}
           className={`px-3 py-1 font-bold text-[10px] rounded border transition-colors ${rendering ? (collapseAlert ? 'bg-red-900/80 text-white border-red-500' : 'bg-teal-900/50 text-teal-400 border-teal-800') : 'bg-slate-800 text-slate-400 border-slate-600'}`}
        >
           {rendering ? 'RENDERING REALITY' : 'PURGE ENTROPY'}
        </button>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex items-center justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)] perspective-[600px]">
         
         {/* 2D Holographic Boundary (The flat surface storing the data) */}
         <div 
            className="absolute w-64 h-64 border-2 border-teal-500/30 rounded-full"
            style={{ 
               transform: 'rotateX(70deg)',
               background: `radial-gradient(circle at center, rgba(20, 184, 166, ${dataDensity/200}) 0%, transparent 70%)`
            }}
         >
            {/* Grid lines on the boundary */}
            <div className="absolute inset-0 bg-[linear-gradient(rgba(20,184,166,0.2)_1px,transparent_1px),linear-gradient(90deg,rgba(20,184,166,0.2)_1px,transparent_1px)] bg-[size:10px_10px] rounded-full [mask-image:radial-gradient(ellipse_at_center,black_40%,transparent_70%)]"></div>
         </div>

         {/* 3D Bulk Projection (The universe popping out) */}
         {rendering && !collapseAlert && (
            <div className="absolute top-[30%] w-24 h-24 flex items-center justify-center">
               <div className="w-16 h-16 border border-teal-400 rounded-lg animate-[spin_4s_linear_infinite]" style={{ transformStyle: 'preserve-3d' }}>
                  <div className="absolute inset-0 border border-teal-400 rounded-lg" style={{ transform: 'rotateY(90deg)' }}></div>
                  <div className="absolute inset-0 border border-teal-400 rounded-lg" style={{ transform: 'rotateX(90deg)' }}></div>
               </div>
            </div>
         )}

         {/* Black Hole Collapse (If Bekenstein bound exceeded) */}
         {collapseAlert && (
            <div className="absolute top-[40%] w-16 h-16 bg-black rounded-full shadow-[0_0_50px_#ef4444] border-2 border-red-500 animate-pulse flex items-center justify-center z-20">
               <div className="absolute w-full h-px bg-red-500/50" style={{ transform: 'rotate(45deg)' }}></div>
               <div className="absolute w-full h-px bg-red-500/50" style={{ transform: 'rotate(-45deg)' }}></div>
            </div>
         )}

         {/* Data Projection beams */}
         <div className="absolute inset-0 flex justify-center opacity-50 mix-blend-screen pointer-events-none">
            {[...Array(15)].map((_, i) => (
               <div 
                  key={i} 
                  className={`w-px absolute bottom-[20%] ${collapseAlert ? 'bg-red-500' : 'bg-teal-400'}`}
                  style={{
                     left: `${30 + Math.random() * 40}%`,
                     height: `${Math.random() * 60}%`,
                     animation: `float-up ${0.5 + Math.random()}s linear infinite`
                  }}
               ></div>
            ))}
         </div>

      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Data Density</div>
            <div className={`text-lg font-mono font-bold ${collapseAlert ? 'text-red-400' : 'text-teal-400'}`}>
               {dataDensity.toFixed(1)} <span className="text-xs text-slate-500">% of Limit</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Bekenstein Bound</div>
            <div className="text-lg font-mono font-bold text-slate-300">
               10<sup className="text-xs">122</sup> <span className="text-xs text-slate-500">Bits</span>
            </div>
         </div>
      </div>

      <div className="w-full bg-slate-950 rounded border border-slate-800 p-2 text-[10px] font-mono text-center">
         <span className={collapseAlert ? 'text-red-400 font-bold animate-pulse' : 'text-emerald-400'}>
            {collapseAlert ? 'BEKENSTEIN BOUND EXCEEDED - BLACK HOLE COLLAPSE' : '3D BULK TO 2D BOUNDARY MAPPING NOMINAL'}
         </span>
      </div>

      <style>{`
        @keyframes float-up {
          0% { transform: translateY(0); opacity: 0; }
          50% { opacity: 1; }
          100% { transform: translateY(-100px); opacity: 0; }
        }
      `}</style>
    </div>
  );
};
