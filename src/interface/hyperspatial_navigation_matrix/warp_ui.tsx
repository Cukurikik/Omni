import React, { useState, useEffect } from 'react';

export const WarpUi: React.FC = () => {
  const [warpFactor, setWarpFactor] = useState(0); // Multiple of c
  const [exoticMatter, setExoticMatter] = useState(0); // kg
  const [jumping, setJumping] = useState(false);

  useEffect(() => {
    let eng: NodeJS.Timeout;

    if (jumping) {
       // Spool up the warp drive
       eng = setInterval(() => {
          setWarpFactor(prev => {
             if (prev < 9.9) return prev + 0.5;
             return 9.9; // Max speed
          });
          setExoticMatter(prev => {
             if (prev > -7000) return prev - 200; // Negative mass
             return -7000;
          });
       }, 200);
    } else {
       // Spool down
       eng = setInterval(() => {
          setWarpFactor(prev => Math.max(0, prev - 1.0));
          setExoticMatter(prev => Math.min(0, prev + 500));
       }, 200);
    }

    return () => clearInterval(eng);
  }, [jumping]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-violet-500">Astrometrics</h2>
          <p className="text-xs text-slate-400">Alcubierre Warp Drive</p>
        </div>
        <button 
           onMouseDown={() => setJumping(true)}
           onMouseUp={() => setJumping(false)}
           onMouseLeave={() => setJumping(false)}
           className={`px-3 py-1 font-bold text-[10px] rounded border transition-all ${jumping ? 'bg-violet-900/80 text-white border-violet-400 shadow-[0_0_20px_#8b5cf6]' : 'bg-slate-800 text-slate-400 border-slate-600 hover:bg-slate-700'}`}
        >
           {jumping ? 'ENGAGE WARP' : 'HOLD TO JUMP'}
        </button>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex flex-col items-center justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)] perspective-[800px]">
         
         {/* Starfield (streaking when warping) */}
         <div className="absolute inset-0 flex items-center justify-center">
            {[...Array(30)].map((_, i) => (
               <div 
                  key={i}
                  className="absolute bg-white rounded-full transition-all duration-75"
                  style={{
                     left: `${Math.random() * 100}%`,
                     top: `${Math.random() * 100}%`,
                     width: jumping ? `${20 + Math.random() * 60}px` : '2px', // Stretch into streaks
                     height: '2px',
                     opacity: Math.random() * 0.8 + 0.2,
                     transform: jumping ? `translateX(-${100 + Math.random() * 200}px)` : 'translateX(0)',
                     animation: jumping ? `warp-stars ${0.2 + Math.random() * 0.3}s linear infinite` : 'none'
                  }}
               ></div>
            ))}
         </div>

         {/* The Starship */}
         <div className="relative z-20 w-16 h-8 bg-slate-400 rounded-full border border-slate-300 shadow-[inset_0_-4px_10px_#1e293b,0_0_15px_#94a3b8]">
            {/* Engine glow */}
            <div className={`absolute -right-2 top-1/2 -translate-y-1/2 w-4 h-4 rounded-full transition-colors duration-300 ${jumping ? 'bg-violet-400 shadow-[0_0_20px_#c084fc]' : 'bg-sky-400/50 shadow-[0_0_5px_#38bdf8]'}`}></div>
         </div>

         {/* The Warp Bubble (bending spacetime) */}
         <div className={`absolute z-10 w-40 h-32 border-4 rounded-[50%] transition-all duration-1000 ${jumping ? 'border-violet-500 shadow-[inset_0_0_30px_#8b5cf6,0_0_40px_#6d28d9] scale-100 opacity-100' : 'border-sky-500/20 scale-75 opacity-0'}`} style={{ transformStyle: 'preserve-3d', transform: 'rotateX(70deg)' }}>
            {/* Spacetime Grid Distortion */}
            <div className="absolute inset-0 rounded-[50%] bg-[radial-gradient(ellipse_at_center,_transparent_40%,_rgba(139,92,246,0.3)_100%)]"></div>
         </div>

         {/* Bow Shock (Blueshift) & Tail (Redshift) */}
         {jumping && (
            <>
               <div className="absolute left-4 w-12 h-32 bg-blue-500/20 blur-xl rounded-full mix-blend-screen"></div>
               <div className="absolute right-4 w-12 h-32 bg-red-500/20 blur-xl rounded-full mix-blend-screen"></div>
            </>
         )}

      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Velocity (Warp Factor)</div>
            <div className={`text-lg font-mono font-bold ${jumping ? 'text-violet-400' : 'text-slate-500'}`}>
               {warpFactor.toFixed(1)}<span className="text-xs">c</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Exotic Mass Required</div>
            <div className="text-lg font-mono font-bold text-red-400">
               {exoticMatter.toFixed(0)} <span className="text-xs text-slate-500">kg</span>
            </div>
         </div>
      </div>

      <div className="w-full bg-slate-950 rounded border border-slate-800 p-2 text-xs font-mono text-center">
         <span className={jumping ? 'text-white' : 'text-slate-500'}>
            {jumping ? 'SPACETIME METRIC COMPRESSED - FTL ACTIVE' : 'SUBLIGHT CRUISING'}
         </span>
      </div>

      <style>{`
        @keyframes warp-stars {
          0% { transform: translateX(200px); }
          100% { transform: translateX(-400px); }
        }
      `}</style>
    </div>
  );
};
