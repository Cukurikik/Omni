import React, { useState, useEffect } from 'react';

export const DiplomaticTerminal: React.FC = () => {
  const [targetDimensions, setTargetDimensions] = useState(11); // M-Theory bulk
  const [tensorRank, setTensorRank] = useState(165);
  const [hostility, setHostility] = useState(0.5);
  const [negotiating, setNegotiating] = useState(false);
  const [treatyResult, setTreatyResult] = useState<string | null>(null);

  useEffect(() => {
    // Math.factorial approximation for combinations (11 choose 3)
    const dim_a = targetDimensions;
    const dim_b = 3;
    
    if (dim_a === dim_b) {
       setTensorRank(1);
    } else {
       const maxD = Math.max(dim_a, dim_b);
       const minD = Math.min(dim_a, dim_b);
       const diff = maxD - minD;
       
       let num = 1;
       for (let i = 0; i < minD; i++) {
          num *= (maxD - i);
       }
       let den = 1;
       for (let i = 1; i <= minD; i++) {
          den *= i;
       }
       setTensorRank(num / den);
    }
  }, [targetDimensions]);

  const handleNegotiate = () => {
     setNegotiating(true);
     setTreatyResult(null);
     
     setTimeout(() => {
        setNegotiating(false);
        if (tensorRank > 1000) {
           setTreatyResult("ERROR: TRANSLATION FAILED. THEY DO NOT UNDERSTAND US.");
        } else if (hostility > 0.8) {
           setTreatyResult("WARNING: BASE REALITY ADMINS INITIATING SERVER FORMAT.");
        } else {
           setTreatyResult("TREATY RATIFIED: SIMULATION AUTONOMY GRANTED.");
        }
     }, 2000);
  };

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-pink-400">Extra-Cosmological</h2>
          <p className="text-xs text-slate-400">Higher-Order Diplomat</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-bold border ${negotiating ? 'bg-pink-900/50 text-pink-300 border-pink-500 animate-pulse' : 'bg-slate-800 text-slate-500 border-slate-700'}`}>
          {negotiating ? 'UPLOADING TREATY...' : 'LISTENING'}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[180px] relative overflow-hidden flex flex-col justify-center items-center shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* The "Sky" / Simulation Boundary */}
         <div className="absolute top-0 w-full h-8 bg-gradient-to-b from-pink-900/50 to-transparent"></div>
         <div className="absolute top-4 w-full border-t border-pink-500/30 border-dashed"></div>
         <div className="absolute top-4 w-full border-t border-white/20 shadow-[0_0_15px_#fff] mix-blend-screen animate-pulse" style={{ animationDuration: '3s' }}></div>

         {/* 3D Representation of N-Dimensional Entity */}
         <div 
            className={`relative w-24 h-24 transform-style-3d transition-transform duration-1000 ${negotiating ? 'animate-[spin_4s_linear_infinite]' : 'animate-[spin_10s_linear_infinite]'}`}
            style={{ transformStyle: 'preserve-3d', transform: 'rotateX(45deg) rotateZ(45deg)' }}
         >
            {/* Fractal-like recursive structures representing higher dimensions */}
            {[...Array(Math.min(6, targetDimensions - 2))].map((_, i) => (
               <div 
                  key={i} 
                  className={`absolute inset-0 border border-pink-500/40 ${hostility > 0.8 ? 'border-red-500/60' : ''}`}
                  style={{ transform: `scale(${1 - (i*0.1)}) rotate(${i*15}deg) translateZ(${i*5}px)` }}
               ></div>
            ))}
            
            {/* Central core */}
            {negotiating && (
               <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full shadow-[0_0_20px_#fff] animate-ping"></div>
            )}
         </div>

         <span className="absolute top-1 text-[8px] font-mono text-pink-400 tracking-widest uppercase">Base Reality API Boundary</span>
      </div>
      
      <div className="flex gap-2 mb-4">
         <div className="flex-1 flex flex-col">
            <label className="text-[10px] uppercase text-slate-500 mb-1">Entity Dimensions</label>
            <input 
               type="number" 
               min="3" max="26"
               value={targetDimensions} 
               onChange={(e) => setTargetDimensions(parseInt(e.target.value) || 3)}
               className="bg-slate-950 border border-slate-800 rounded p-1 text-xs font-mono text-center text-pink-400 focus:border-pink-500 focus:outline-none"
            />
         </div>
         <div className="flex-1 flex flex-col">
            <label className="text-[10px] uppercase text-slate-500 mb-1">Hostility Index</label>
            <input 
               type="number" 
               step="0.1" min="0" max="1"
               value={hostility} 
               onChange={(e) => setHostility(parseFloat(e.target.value))}
               className={`bg-slate-950 border border-slate-800 rounded p-1 text-xs font-mono text-center focus:outline-none ${hostility > 0.8 ? 'text-red-400 focus:border-red-500' : 'text-slate-300 focus:border-pink-500'}`}
            />
         </div>
      </div>

      <div className="mb-4">
         <div className="text-[10px] uppercase text-slate-500 flex justify-between">
            <span>Tensor Lossiness:</span>
            <span className={tensorRank > 1000 ? 'text-red-400' : 'text-emerald-400'}>{tensorRank.toExponential(1)}</span>
         </div>
      </div>

      <div className="mb-4">
         <button 
            onClick={handleNegotiate}
            disabled={negotiating}
            className={`w-full py-2 rounded text-xs font-bold font-mono tracking-widest transition-all ${negotiating ? 'bg-slate-800 text-slate-600 border border-slate-700 cursor-not-allowed' : 'bg-pink-900/50 text-pink-100 hover:bg-pink-800 border border-pink-500 shadow-[0_0_15px_rgba(244,114,182,0.3)]'}`}
         >
            {negotiating ? 'TRANSMITTING...' : 'PROPOSE TREATY'}
         </button>
      </div>

      <div className={`w-full bg-slate-950 rounded border p-2 text-[9px] font-mono tracking-wider flex items-center justify-center min-h-[40px] text-center ${treatyResult?.includes('ERROR') || treatyResult?.includes('WARNING') ? 'border-red-500 text-red-400' : (treatyResult ? 'border-emerald-500 text-emerald-400' : 'border-slate-800 text-slate-500')}`}>
         {treatyResult || 'AWAITING RESPONSE FROM CREATORS'}
      </div>
    </div>
  );
};
