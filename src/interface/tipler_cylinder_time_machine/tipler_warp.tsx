import React, { useState, useEffect } from 'react';

export const TiplerWarp: React.FC = () => {
  const [spinVelocity, setSpinVelocity] = useState(0); // % of c
  const [temporalShift, setTemporalShift] = useState(0); // Years into the past
  const [ctcActive, setCtcActive] = useState(false);
  const [collapseRisk, setCollapseRisk] = useState(false);

  useEffect(() => {
    let cylinder: NodeJS.Timeout;

    if (ctcActive) {
       // Spin up the cylinder
       cylinder = setInterval(() => {
          setSpinVelocity(prev => {
             const next = prev + 0.05;
             if (next > 0.5) { // Needs to spin at > 50% speed of light
                // Spacetime frame-dragging initiates time travel
                setTemporalShift(t => t - 10); // Traveling back in time
             }
             if (next > 0.8) setCollapseRisk(true); // Spinning too fast risks tearing the cylinder apart
             return Math.min(0.9, next);
          });
       }, 100);
    } else {
       // Spin down
       cylinder = setInterval(() => {
          setSpinVelocity(prev => Math.max(0, prev - 0.1));
          setCollapseRisk(false);
       }, 100);
    }

    return () => clearInterval(cylinder);
  }, [ctcActive]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-indigo-400">Temporal Engine</h2>
          <p className="text-xs text-slate-400">Tipler Cylinder</p>
        </div>
        <button 
           onMouseDown={() => setCtcActive(true)}
           onMouseUp={() => setCtcActive(false)}
           onMouseLeave={() => setCtcActive(false)}
           className={`px-3 py-1 font-bold text-[10px] rounded border transition-all ${ctcActive ? 'bg-indigo-900/80 text-white border-indigo-400 shadow-[0_0_20px_#818cf8]' : 'bg-slate-800 text-slate-400 border-slate-600 hover:bg-slate-700'}`}
        >
           {ctcActive ? 'FRAME-DRAGGING' : 'INITIATE SPIN'}
        </button>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex items-center justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)] perspective-[800px]">
         
         {/* The Tipler Cylinder (Infinitely long dense matter) */}
         <div 
            className={`absolute w-12 h-64 bg-slate-400 shadow-[inset_0_0_20px_#0f172a,0_0_30px_#818cf8] border-x border-slate-300 ${collapseRisk ? 'animate-pulse bg-red-400' : ''}`}
            style={{ 
               transform: 'rotateX(60deg) rotateZ(30deg)',
               background: 'repeating-linear-gradient(to bottom, #94a3b8, #94a3b8 10px, #cbd5e1 10px, #cbd5e1 20px)'
            }}
         >
            {/* Spin blur effect */}
            <div className="absolute inset-0 bg-black/20" style={{ opacity: spinVelocity }}></div>
         </div>

         {/* Spacetime Frame-Dragging Vortex */}
         {spinVelocity > 0 && (
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
               {[...Array(5)].map((_, i) => (
                  <div 
                     key={i}
                     className="absolute border border-indigo-500/50 rounded-[50%]"
                     style={{
                        width: `${40 + i * 40}px`,
                        height: `${20 + i * 20}px`,
                        transform: `rotateX(60deg) rotateZ(${30 + spinVelocity * 100}deg)`,
                        boxShadow: spinVelocity > 0.5 ? '0 0 10px #818cf8' : 'none',
                        transition: 'transform 0.1s linear'
                     }}
                  ></div>
               ))}
            </div>
         )}

         {/* The Spacecraft (Navigating the CTC) */}
         {spinVelocity > 0.5 && (
            <div 
               className="absolute w-3 h-3 bg-white rounded-full shadow-[0_0_10px_#fff]"
               style={{
                  left: '50%',
                  top: '50%',
                  transformOrigin: '-40px 0',
                  animation: 'spin 1s linear infinite reverse'
               }}
            ></div>
         )}
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Rotational Velocity</div>
            <div className={`text-lg font-mono font-bold ${collapseRisk ? 'text-red-400' : 'text-indigo-400'}`}>
               {(spinVelocity * 100).toFixed(1)} <span className="text-xs">% c</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Temporal Shift</div>
            <div className="text-lg font-mono font-bold text-white">
               {temporalShift} <span className="text-xs text-slate-500">Years</span>
            </div>
         </div>
      </div>

      <div className="w-full bg-slate-950 rounded border border-slate-800 p-2 text-xs font-mono text-center">
         <span className={collapseRisk ? 'text-red-400' : (spinVelocity > 0.5 ? 'text-emerald-400' : 'text-slate-500')}>
            {collapseRisk ? 'WARNING: CYLINDER COLLAPSING INTO BLACK HOLE' : (spinVelocity > 0.5 ? 'CLOSED TIMELIKE CURVE ESTABLISHED' : 'SUBLIGHT SPIN - NO TEMPORAL EFFECT')}
         </span>
      </div>

      <style>{`
        @keyframes spin { 100% { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
};
