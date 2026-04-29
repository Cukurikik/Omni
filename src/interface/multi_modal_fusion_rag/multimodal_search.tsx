import React, { useState, useEffect } from 'react';

export const MultimodalSearch: React.FC = () => {
  const [fused, setFused] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setFused(true);
    }, 2000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 flex justify-between items-center border-b border-slate-700 pb-2">
        <h2 className="text-xl font-bold text-fuchsia-400">Multimodal RAG</h2>
        <span className="text-[10px] bg-slate-800 px-2 py-1 rounded text-slate-400">CLIP + LLM</span>
      </div>

      <div className="flex gap-4 mb-6">
         {/* Image Input Simulation */}
         <div className="flex-1 bg-slate-800 rounded border border-slate-600 aspect-square flex flex-col items-center justify-center p-2 relative overflow-hidden group">
            <div className="text-3xl mb-1 transition-transform group-hover:scale-110">📸</div>
            <div className="text-[8px] uppercase text-slate-400 font-mono">Image Embed</div>
            
            {/* Scanline effect */}
            <div className="absolute top-0 left-0 right-0 h-0.5 bg-fuchsia-500/50 animate-[scan_2s_ease-in-out_infinite]"></div>
         </div>
         
         {/* Text Input Simulation */}
         <div className="flex-1 bg-slate-800 rounded border border-slate-600 aspect-square flex flex-col items-center justify-center p-2">
            <div className="text-3xl mb-1 text-slate-400">"..."</div>
            <div className="text-[8px] uppercase text-slate-400 font-mono text-center">"Identify this defect"</div>
         </div>
      </div>
      
      <div className="flex flex-col items-center">
         <div className={`text-xl transition-all duration-500 ${fused ? 'text-fuchsia-400 scale-125' : 'text-slate-600'}`}>↓</div>
         
         <div className={`mt-2 p-3 w-full rounded border text-center transition-all duration-700 ${fused ? 'bg-fuchsia-900/30 border-fuchsia-500 shadow-[0_0_15px_rgba(217,70,239,0.2)]' : 'bg-slate-950 border-slate-800'}`}>
            <div className="text-[10px] uppercase font-bold text-fuchsia-500 mb-1">Fused Vector Space</div>
            <div className="text-xs font-mono text-white">
               {fused ? '[0.41, -0.82, 0.11 ... 0.94]' : 'Awaiting modalities...'}
            </div>
         </div>
      </div>
    </div>
  );
};
