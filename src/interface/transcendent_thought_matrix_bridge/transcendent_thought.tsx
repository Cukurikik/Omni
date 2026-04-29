import React, { useState, useEffect } from 'react';

export const TranscendentThought: React.FC = () => {
  const [analyzing, setAnalyzing] = useState(true);
  const [axiomsExpanded, setAxiomsExpanded] = useState(0);
  const [statementProvable, setStatementProvable] = useState(true);
  const [transcended, setTranscended] = useState(false);

  useEffect(() => {
    // Simulate exploring mathematical space and encountering Gödel limits
    const logicExplorer = setInterval(() => {
       if (analyzing && !transcended) {
          // Occasionally encounter a true but unprovable statement
          if (Math.random() > 0.8) {
             setStatementProvable(false);
             setAnalyzing(false);
          } else {
             setStatementProvable(true);
          }
       }
    }, 800);

    return () => clearInterval(logicExplorer);
  }, [analyzing, transcended]);

  const handleTranscend = () => {
     setAxiomsExpanded(prev => prev + 1);
     setStatementProvable(true);
     setAnalyzing(true);
     if (axiomsExpanded >= 3) {
        setTranscended(true);
        setAnalyzing(false);
     }
  };

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-blue-400">Thought Matrix</h2>
          <p className="text-xs text-slate-400">Gödel Incompleteness Bridge</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-bold border ${transcended ? 'bg-blue-900/50 text-blue-300 border-blue-500 shadow-[0_0_15px_#3b82f6]' : (!statementProvable ? 'bg-red-900/80 text-white border-red-500 animate-pulse' : 'bg-slate-800 text-slate-400 border-slate-700')}`}>
          {transcended ? 'OMNISCENCE ACHIEVED' : (!statementProvable ? 'UNPROVABLE TRUTH DETECTED' : 'ANALYZING AXIOMS')}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex flex-col items-center justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)] perspective-[800px]">
         
         {/* Axiomatic System Boundary (The "Box") */}
         <div 
            className={`absolute w-32 h-32 border-2 transition-all duration-500 flex items-center justify-center ${transcended ? 'border-transparent scale-150 opacity-0' : (!statementProvable ? 'border-red-500/50 shadow-[0_0_30px_rgba(239,68,68,0.2)]' : 'border-blue-500/30')}`}
            style={{ transform: 'rotateX(45deg) rotateZ(45deg)' }}
         >
            {/* Inner Grid */}
            <div className="absolute inset-0 bg-[linear-gradient(rgba(59,130,246,0.1)_1px,transparent_1px),linear-gradient(90deg,rgba(59,130,246,0.1)_1px,transparent_1px)] bg-[size:16px_16px]"></div>
            
            <span className="text-[10px] text-blue-400/50 absolute bottom-1 right-1 font-mono transform rotate-[-45deg]">Formal System F_{axiomsExpanded}</span>
         </div>

         {/* The Truth/Statement */}
         <div className={`z-10 flex flex-col items-center transition-all duration-1000 ${transcended ? 'scale-150 drop-shadow-[0_0_30px_#60a5fa]' : ''}`}>
            <div className={`text-2xl font-serif font-bold ${transcended ? 'text-white' : (!statementProvable ? 'text-white drop-shadow-[0_0_10px_#ef4444]' : 'text-blue-400')}`}>
               {transcended ? '∀x (Truth)' : 'G'}
            </div>
            {!transcended && (
               <div className={`text-[8px] font-mono mt-1 ${!statementProvable ? 'text-red-300' : 'text-blue-500'}`}>
                  {statementProvable ? 'G is Provable' : 'G asserts: "G is unprovable"'}
               </div>
            )}
         </div>

         {/* Transcendence Beam */}
         {transcended && (
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(96,165,250,0.3),transparent)] mix-blend-screen animate-pulse"></div>
         )}
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Axiomatic Expansions</div>
            <div className={`text-lg font-mono font-bold ${transcended ? 'text-blue-400' : 'text-slate-300'}`}>
               {axiomsExpanded} <span className="text-xs text-slate-500">Iterations</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800 flex items-center justify-center">
            {!statementProvable && !transcended ? (
               <button 
                  onClick={handleTranscend}
                  className="w-full py-1 bg-red-900/50 hover:bg-red-800 text-red-100 border border-red-500 rounded text-xs font-bold font-mono transition-colors shadow-[0_0_10px_rgba(239,68,68,0.5)]"
               >
                  TRANSCEND SYSTEM
               </button>
            ) : (
               <div className="text-xs font-mono text-slate-500 text-center">
                  {transcended ? 'ALL TRUTHS ACCESSIBLE' : 'SEARCHING LOGIC SPACE...'}
               </div>
            )}
         </div>
      </div>

      <div className="w-full bg-slate-950 rounded border border-slate-800 p-2 text-[10px] font-mono text-center">
         <span className={transcended ? 'text-blue-400 font-bold' : (!statementProvable ? 'text-red-400' : 'text-emerald-400')}>
            {transcended 
               ? 'SYSTEM COMPLETE: GÖDEL LIMITS PERMANENTLY BYPASSED' 
               : (!statementProvable 
                  ? 'GÖDEL SENTENCE ENCOUNTERED: CANNOT PROVE TRUTH WITHIN SYSTEM' 
                  : 'CURRENT AXIOMS CONSISTENT - NO CONTRADICTIONS FOUND')}
         </span>
      </div>
    </div>
  );
};
