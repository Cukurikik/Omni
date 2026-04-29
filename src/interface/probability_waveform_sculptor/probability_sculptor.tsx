import React, { useState, useEffect } from 'react';

export const ProbabilitySculptor: React.FC = () => {
  const [naturalProb, setNaturalProb] = useState(1e-10);
  const [targetProb, setTargetProb] = useState(1.0);
  const [energyRequired, setEnergyRequired] = useState(0); // Exajoules
  const [availableEnergy] = useState(5000); // 5000 Exajoules available
  const [sculpting, setSculpting] = useState(false);
  const [miracleResult, setMiracleResult] = useState<string | null>(null);

  useEffect(() => {
    // Energy cost = -ln(natural_probability) * target_probability * 100
    if (naturalProb > 0 && targetProb > 0) {
       const cost = -Math.log(naturalProb) * targetProb * 100;
       setEnergyRequired(cost);
    } else {
       setEnergyRequired(0);
    }
  }, [naturalProb, targetProb]);

  const handleSculpt = () => {
     setSculpting(true);
     setMiracleResult(null);
     
     setTimeout(() => {
        setSculpting(false);
        if (energyRequired > availableEnergy) {
           setMiracleResult("INSUFFICIENT ENERGY: Miracle denied.");
        } else {
           setMiracleResult(`MIRACLE ORCHESTRATED: 1 in ${Math.round(1/naturalProb).toExponential(1)} event forced.`);
        }
     }, 1500);
  };

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-yellow-400">Waveform Sculptor</h2>
          <p className="text-xs text-slate-400">Probability Override</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-bold border ${sculpting ? 'bg-yellow-900/50 text-yellow-300 border-yellow-500 animate-pulse' : 'bg-slate-800 text-slate-500 border-slate-700'}`}>
          {sculpting ? 'COLLAPSING WAVEFORM...' : 'STOCHASTIC'}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[180px] relative overflow-hidden flex flex-col justify-center items-center shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* Background Gaussian Curve (Natural Probability) */}
         <svg className="absolute bottom-0 w-full h-32 opacity-30" viewBox="0 0 100 100" preserveAspectRatio="none">
            <path d="M0,100 Q20,100 35,50 T50,10 T65,50 T80,100 L100,100 L0,100 Z" fill="rgba(250,204,21,0.2)" />
            <path d="M0,100 Q20,100 35,50 T50,10 T65,50 T80,100 L100,100 Z" fill="none" stroke="#facc15" strokeWidth="1" />
         </svg>

         {/* The Target Event (Far out on the tail) */}
         <div 
            className={`absolute bottom-4 right-8 w-2 h-2 rounded-full transition-all duration-1000 ${sculpting ? 'bg-white shadow-[0_0_20px_#fff,0_0_40px_#facc15] scale-[5]' : 'bg-yellow-600 shadow-[0_0_5px_#ca8a04]'}`}
         ></div>

         {/* The "Miracle" Force */}
         {sculpting && (
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_right,rgba(250,204,21,0.4),transparent_70%)] mix-blend-screen animate-pulse"></div>
         )}
      </div>
      
      <div className="flex gap-2 mb-4">
         <div className="flex-1 flex flex-col">
            <label className="text-[10px] uppercase text-slate-500 mb-1">Nat. Prob (e.g. 1e-10)</label>
            <input 
               type="number" 
               step="1e-5"
               value={naturalProb} 
               onChange={(e) => setNaturalProb(parseFloat(e.target.value))}
               className="bg-slate-950 border border-slate-800 rounded p-1 text-xs font-mono text-center focus:border-yellow-500 focus:outline-none"
            />
         </div>
         <div className="flex-1 flex flex-col">
            <label className="text-[10px] uppercase text-yellow-500 mb-1">Target Prob (0-1)</label>
            <input 
               type="number" 
               step="0.1"
               min="0"
               max="1"
               value={targetProb} 
               onChange={(e) => setTargetProb(parseFloat(e.target.value))}
               className="bg-slate-950 border border-yellow-800 rounded p-1 text-xs font-mono text-center text-white focus:border-yellow-400 focus:outline-none"
            />
         </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Energy Required</div>
            <div className={`text-lg font-mono font-bold ${energyRequired > availableEnergy ? 'text-red-400' : 'text-yellow-400'}`}>
               {energyRequired.toFixed(0)} <span className="text-[10px] text-slate-500">EJ</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Local Grid Avail.</div>
            <div className="text-lg font-mono font-bold text-slate-300">
               {availableEnergy} <span className="text-[10px] text-slate-500">EJ</span>
            </div>
         </div>
      </div>

      <div className="mb-4">
         <button 
            onClick={handleSculpt}
            disabled={sculpting || energyRequired > availableEnergy}
            className={`w-full py-2 rounded text-xs font-bold font-mono tracking-widest transition-all ${sculpting || energyRequired > availableEnergy ? 'bg-slate-800 text-slate-600 border border-slate-700 cursor-not-allowed' : 'bg-yellow-900/50 text-yellow-100 hover:bg-yellow-800 border border-yellow-500 shadow-[0_0_15px_rgba(234,179,8,0.3)]'}`}
         >
            {sculpting ? 'OVERRIDING BORN RULE...' : 'ORCHESTRATE MIRACLE'}
         </button>
      </div>

      <div className={`w-full bg-slate-950 rounded border p-2 text-[9px] font-mono tracking-wider flex items-center justify-center min-h-[40px] text-center ${miracleResult?.includes('INSUFFICIENT') ? 'border-red-500 text-red-400' : (miracleResult ? 'border-emerald-500 text-emerald-400' : 'border-slate-800 text-slate-500')}`}>
         {miracleResult || 'READY TO ALTER CAUSAL PROBABILITIES'}
      </div>
    </div>
  );
};
