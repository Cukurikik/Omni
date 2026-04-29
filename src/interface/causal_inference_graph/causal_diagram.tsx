import React, { useState, useEffect } from 'react';

export const CausalDiagram: React.FC = () => {
  const [intervention, setIntervention] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setIntervention(prev => !prev);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-amber-400">Causal AI Graph</h2>
        <p className="text-xs text-slate-400">Pearl's Do-Calculus Reasoning</p>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 h-[180px] relative flex items-center justify-center">
         
         {/* Confounder Node (Z) */}
         <div className="absolute top-[20%] left-[50%] transform -translate-x-1/2 w-16 h-8 bg-slate-800 rounded-full border border-slate-500 flex items-center justify-center text-[10px] font-bold z-10">
            Season (Z)
         </div>

         {/* Cause Node (X) */}
         <div className={`absolute top-[60%] left-[20%] w-20 h-10 rounded-lg border-2 flex items-center justify-center text-[10px] font-bold z-10 transition-all duration-500 ${intervention ? 'bg-emerald-900/80 border-emerald-500 text-emerald-300 shadow-[0_0_15px_rgba(16,185,129,0.5)]' : 'bg-slate-800 border-slate-500'}`}>
            {intervention ? 'do(Ice Cream=0)' : 'Ice Cream (X)'}
         </div>

         {/* Effect Node (Y) */}
         <div className="absolute top-[60%] right-[20%] w-20 h-10 bg-slate-800 rounded-lg border border-slate-500 flex flex-col items-center justify-center text-[10px] font-bold z-10">
            <div>Shark Atk (Y)</div>
            <div className={`text-[8px] font-mono transition-colors ${intervention ? 'text-slate-400' : 'text-amber-400'}`}>P={intervention ? '0.02' : '0.15'}</div>
         </div>

         {/* Edges */}
         {/* Z -> X */}
         {!intervention && (
            <svg className="absolute inset-0 w-full h-full pointer-events-none">
              <line x1="50%" y1="35%" x2="30%" y2="60%" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrow)" strokeDasharray="4" />
            </svg>
         )}
         
         {/* Z -> Y */}
         <svg className="absolute inset-0 w-full h-full pointer-events-none">
           <line x1="50%" y1="35%" x2="70%" y2="60%" stroke="#64748b" strokeWidth="2" markerEnd="url(#arrow)" />
         </svg>

         {/* SVG Defs for arrows */}
         <svg width="0" height="0">
           <defs>
             <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">
               <path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b" />
             </marker>
           </defs>
         </svg>
      </div>
      
      <div className="mt-3 p-2 bg-amber-900/20 border border-amber-900/50 rounded text-[10px] text-amber-200 font-mono">
         LLM Insight: {intervention ? "Performing do-intervention. Correlation broken. True causal ATE is ~0." : "Observational correlation detected, but confounded by Season."}
      </div>
    </div>
  );
};
