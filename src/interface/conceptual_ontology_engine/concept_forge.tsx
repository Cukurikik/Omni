import React, { useState, useEffect } from 'react';

export const ConceptForge: React.FC = () => {
  const [conceptA, setConceptA] = useState('Gravity');
  const [conceptB, setConceptB] = useState('Love');
  const [distance, setDistance] = useState(0.85); // Too far
  const [forging, setForging] = useState(false);
  const [forgeResult, setForgeResult] = useState<string | null>(null);

  // Auto-calculate rough "semantic distance" based on string length diff for UI purposes
  useEffect(() => {
     const lenDiff = Math.abs(conceptA.length - conceptB.length);
     // If they are the same word
     if (conceptA.toLowerCase() === conceptB.toLowerCase()) {
        setDistance(0.05);
     } else if (conceptA === 'Gravity' && conceptB === 'Love') {
        setDistance(0.85); // Hardcoded dissonance example
     } else if (conceptA === 'Time' && conceptB === 'Memory') {
        setDistance(0.4); // Good synthesis example
     } else {
        setDistance(Math.min(0.9, 0.2 + (lenDiff * 0.1)));
     }
  }, [conceptA, conceptB]);

  const handleForge = () => {
     setForging(true);
     setForgeResult(null);
     
     setTimeout(() => {
        setForging(false);
        if (distance > 0.8) {
           setForgeResult("DISSONANCE: Concepts mutually exclusive.");
        } else if (distance < 0.1) {
           setForgeResult("REDUNDANT: Concepts are identical.");
        } else {
           setForgeResult(`SYNTHESIS: New Platonic Form materialized.`);
        }
     }, 1500);
  };

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-indigo-400">Concept Forge</h2>
          <p className="text-xs text-slate-400">Ontological Synthesis</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-bold border ${forging ? 'bg-indigo-900/50 text-indigo-300 border-indigo-500 animate-pulse' : 'bg-slate-800 text-slate-500 border-slate-700'}`}>
          {forging ? 'MATERIALIZING...' : 'READY'}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[180px] relative overflow-hidden flex items-center justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* Concept A Node */}
         <div 
            className={`absolute w-16 h-16 rounded-full border-2 border-indigo-500/50 bg-indigo-900/30 flex items-center justify-center transition-all duration-1000 ${forging ? 'translate-x-8' : '-translate-x-12'}`}
         >
            <span className="text-[10px] font-bold text-indigo-300">{conceptA}</span>
         </div>

         {/* Concept B Node */}
         <div 
            className={`absolute w-16 h-16 rounded-full border-2 border-fuchsia-500/50 bg-fuchsia-900/30 flex items-center justify-center transition-all duration-1000 ${forging ? '-translate-x-8' : 'translate-x-12'}`}
         >
            <span className="text-[10px] font-bold text-fuchsia-300">{conceptB}</span>
         </div>

         {/* Collision / Synthesis Spark */}
         {forging && (
            <div className="absolute w-8 h-8 rounded-full bg-white shadow-[0_0_30px_#fff] mix-blend-screen animate-[ping_0.5s_ease-out_infinite] z-10"></div>
         )}
         
         {/* Success Ring */}
         {!forging && forgeResult?.includes('SYNTHESIS') && (
            <div className="absolute w-24 h-24 rounded-full border-4 border-emerald-400 shadow-[0_0_20px_#34d399] animate-[ping_1s_ease-out_forwards]"></div>
         )}
      </div>
      
      <div className="flex gap-2 mb-4">
         <input 
            type="text" 
            value={conceptA} 
            onChange={(e) => setConceptA(e.target.value)}
            className="flex-1 bg-slate-950 border border-slate-800 rounded p-2 text-xs font-mono text-center focus:border-indigo-500 focus:outline-none"
            placeholder="Concept A"
         />
         <div className="flex items-center text-slate-500 font-mono text-xs">+</div>
         <input 
            type="text" 
            value={conceptB} 
            onChange={(e) => setConceptB(e.target.value)}
            className="flex-1 bg-slate-950 border border-slate-800 rounded p-2 text-xs font-mono text-center focus:border-fuchsia-500 focus:outline-none"
            placeholder="Concept B"
         />
      </div>

      <div className="mb-4 flex items-center justify-between">
         <span className="text-[10px] uppercase text-slate-500">Semantic Distance</span>
         <span className={`text-xs font-mono font-bold ${distance > 0.8 ? 'text-red-400' : (distance < 0.1 ? 'text-amber-400' : 'text-emerald-400')}`}>
            {distance.toFixed(2)}
         </span>
      </div>

      <div className="mb-4">
         <button 
            onClick={handleForge}
            disabled={forging || !conceptA || !conceptB}
            className={`w-full py-2 rounded text-xs font-bold font-mono tracking-widest transition-all ${forging || !conceptA || !conceptB ? 'bg-slate-800 text-slate-600 border border-slate-700 cursor-not-allowed' : 'bg-indigo-900/50 text-indigo-100 hover:bg-indigo-800 border border-indigo-500 shadow-[0_0_15px_rgba(99,102,241,0.3)]'}`}
         >
            {forging ? 'FUSING MEANING...' : 'SYNTHESIZE CONCEPTS'}
         </button>
      </div>

      <div className={`w-full bg-slate-950 rounded border p-2 text-[9px] font-mono tracking-wider flex items-center justify-center min-h-[40px] ${forgeResult?.includes('DISSONANCE') ? 'border-red-500 text-red-400' : (forgeResult?.includes('REDUNDANT') ? 'border-amber-500 text-amber-400' : (forgeResult ? 'border-emerald-500 text-emerald-400' : 'border-slate-800 text-slate-500'))}`}>
         {forgeResult || 'AWAITING ONTOLOGICAL INPUT'}
      </div>
    </div>
  );
};
