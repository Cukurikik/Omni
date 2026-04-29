import React, { useState, useEffect } from 'react';

export const GenesisSeed: React.FC = () => {
  const [alpha, setAlpha] = useState(1/137.035999); // Fine structure constant
  const [igniting, setIgniting] = useState(false);
  const [universeRadius, setUniverseRadius] = useState(0);
  const [anthropicFailure, setAnthropicFailure] = useState(false);

  // Target optimal alpha
  const optimalAlpha = 1/137.035999;
  const variance = Math.abs(alpha - optimalAlpha) / optimalAlpha;

  useEffect(() => {
    let inflation: NodeJS.Timeout;

    if (igniting) {
       if (variance > 0.04) {
          setAnthropicFailure(true);
          setIgniting(false);
       } else {
          setAnthropicFailure(false);
          // Cosmic Inflation! Exponential growth
          inflation = setInterval(() => {
             setUniverseRadius(prev => {
                if (prev === 0) return 1e-35; // Planck length
                const next = prev * 1.5; // Exponential inflation
                if (next > 1e26) return 1e26; // Stop at macroscopic size for UI
                return next;
             });
          }, 50);
       }
    } else {
       setUniverseRadius(0);
    }

    return () => clearInterval(inflation);
  }, [igniting, alpha, variance]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-emerald-400">Genesis Seed</h2>
          <p className="text-xs text-slate-400">Pocket Universe Nucleation</p>
        </div>
        <button 
           onClick={() => setIgniting(!igniting)}
           disabled={anthropicFailure && !igniting}
           className={`px-3 py-1 font-bold text-[10px] rounded border transition-colors ${igniting ? 'bg-emerald-900/80 text-emerald-300 border-emerald-500 shadow-[0_0_15px_#10b981]' : (anthropicFailure ? 'bg-slate-800 text-slate-600 border-slate-700 cursor-not-allowed' : 'bg-slate-800 text-emerald-500 border-emerald-700 hover:bg-emerald-900/30')}`}
        >
           {igniting ? 'INFLATING' : 'IGNITE BIG BANG'}
        </button>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex items-center justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* Vacuum Chamber Bounds */}
         <div className="absolute inset-0 border-[8px] border-slate-800/50 rounded-lg"></div>

         {/* The Nucleation Bubble / New Universe */}
         {universeRadius > 0 && (
            <div 
               className="absolute rounded-full border border-white flex items-center justify-center mix-blend-screen"
               style={{
                  width: `${Math.max(2, Math.min(300, Math.log10(universeRadius) * 5 + 180))}px`,
                  height: `${Math.max(2, Math.min(300, Math.log10(universeRadius) * 5 + 180))}px`,
                  background: 'radial-gradient(circle at center, rgba(16,185,129,0.8) 0%, rgba(16,185,129,0.2) 50%, transparent 100%)',
                  boxShadow: '0 0 50px #10b981, inset 0 0 30px #fff'
               }}
            >
               {/* Cosmic Microwave Background within the bubble */}
               {universeRadius > 1 && (
                  <div className="absolute inset-0 rounded-full opacity-30" style={{ background: 'url("data:image/svg+xml,%3Csvg viewBox=\'0 0 200 200\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cfilter id=\'noiseFilter\'%3E%3CfeTurbulence type=\'fractalNoise\' baseFrequency=\'0.85\' numOctaves=\'3\' stitchTiles=\'stitch\'/%3E%3C/filter%3E%3Crect width=\'100%25\' height=\'100%25\' filter=\'url(%23noiseFilter)\'/%3E%3C/svg%3E")' }}></div>
               )}
            </div>
         )}

         {/* Higgs Field Perturbation Laser */}
         {igniting && universeRadius === 1e-35 && (
            <div className="absolute top-0 bottom-1/2 w-1 bg-white shadow-[0_0_20px_#fff] animate-pulse"></div>
         )}
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800 flex flex-col justify-center">
            <div className="flex justify-between items-center mb-1">
               <span className="text-[9px] uppercase text-slate-500">Fine-Structure (α)</span>
               <span className="text-[9px] text-slate-500">1/137.036</span>
            </div>
            <input 
               type="range" 
               min={1/145} 
               max={1/130} 
               step={0.0001} 
               value={alpha} 
               onChange={(e) => {
                  setAlpha(parseFloat(e.target.value));
                  if (igniting) setIgniting(false);
               }}
               className="w-full accent-emerald-500"
            />
            <div className="text-center mt-1 text-xs font-mono">
               {alpha.toExponential(4)}
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Universe Radius</div>
            <div className={`text-lg font-mono font-bold ${universeRadius > 1e10 ? 'text-emerald-400' : 'text-slate-300'}`}>
               {universeRadius === 0 ? '0' : `10^${Math.log10(universeRadius).toFixed(0)}`} <span className="text-xs text-slate-500">m</span>
            </div>
         </div>
      </div>

      <div className="w-full bg-slate-950 rounded border border-slate-800 p-2 text-[10px] font-mono text-center">
         <span className={anthropicFailure ? 'text-red-400 font-bold' : (variance > 0.01 ? 'text-amber-400' : 'text-emerald-400')}>
            {anthropicFailure 
               ? 'ANTHROPIC FAILURE: STARS CANNOT IGNITE' 
               : (variance > 0.01 
                  ? 'WARNING: STELLAR LIFESPANS SEVERELY REDUCED' 
                  : (igniting ? 'COSMIC INFLATION ACTIVE' : 'PARAMETERS OPTIMAL - READY FOR GENESIS'))}
         </span>
      </div>
    </div>
  );
};
