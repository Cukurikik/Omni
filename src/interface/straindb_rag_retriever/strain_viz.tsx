import React, { useState, useEffect } from 'react';

export const StrainViz: React.FC = () => {
  const [similarity, setSimilarity] = useState(0.85);

  useEffect(() => {
    // Simulate RAG retrieving a closer genome match
    const timer = setTimeout(() => {
      setSimilarity(0.96);
    }, 2000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 border-b border-slate-700 pb-2">
        <h2 className="text-xl font-bold text-teal-400">StrainsDB RAG</h2>
        <p className="text-xs text-slate-400">Genomic Sequence Retriever</p>
      </div>

      <div className="flex justify-between items-center mb-6">
         <div className="text-center">
            <div className="w-12 h-12 rounded-full bg-slate-800 border-2 border-teal-500 mx-auto flex items-center justify-center font-bold text-xs text-teal-300">Q</div>
            <div className="text-[10px] text-slate-500 mt-1 uppercase">Query Strain</div>
         </div>
         
         <div className="flex-1 flex flex-col items-center justify-center px-4">
             <div className="text-xs font-mono text-teal-400 mb-1">ANI: {(similarity * 100).toFixed(1)}%</div>
             <div className="w-full h-px bg-slate-700 relative">
                 <div className="absolute top-1/2 left-0 right-0 border-t border-teal-500 border-dashed transform -translate-y-1/2 transition-all duration-1000"></div>
             </div>
             <div className="text-[10px] text-slate-500 mt-1">Retrieving Matches...</div>
         </div>

         <div className="text-center">
            <div className="w-12 h-12 rounded-full bg-slate-800 border-2 border-fuchsia-500 mx-auto flex items-center justify-center font-bold text-xs text-fuchsia-300">DB</div>
            <div className="text-[10px] text-slate-500 mt-1 uppercase">StrainsDB</div>
         </div>
      </div>

      <div className="bg-slate-950 p-3 rounded border border-slate-800">
         <div className="text-xs text-slate-400 mb-1">LLM Generated Insight:</div>
         <div className="text-sm font-mono text-white leading-tight">
             {similarity >= 0.95 
               ? "Based on an ANI of >95%, the query isolate belongs to the same species as the retrieved StrainsDB reference."
               : "Query sequence aligns with genus-level references but lacks species-level identity."}
         </div>
      </div>
    </div>
  );
};
