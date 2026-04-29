import React, { useState, useEffect } from 'react';

export const CrystalArchiveUi: React.FC = () => {
  const [writeProgress, setWriteProgress] = useState(0);
  const [pageData, setPageData] = useState<number[]>([]);

  useEffect(() => {
    // Simulate writing "pages" to the holographic crystal
    const writer = setInterval(() => {
      setWriteProgress(prev => {
         if (prev >= 100) return 0; // Reset for loop
         return prev + 2;
      });
      
      // Generate random 1s and 0s for the SLM visualizer
      const newPage = Array.from({length: 64}, () => Math.random() > 0.5 ? 1 : 0);
      setPageData(newPage);
      
    }, 100);

    return () => clearInterval(writer);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-cyan-400">Crystal Archive</h2>
          <p className="text-xs text-slate-400">Volumetric Holographic Storage</p>
        </div>
        <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_#10b981] animate-pulse"></div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[180px] flex items-center justify-between relative">
         
         {/* Laser Source */}
         <div className="w-4 h-8 bg-slate-700 border border-slate-600 rounded flex items-center">
            <div className="w-full h-1 bg-cyan-400 shadow-[0_0_15px_#22d3ee]"></div>
         </div>
         
         {/* Spatial Light Modulator (SLM) - Data Page */}
         <div className="w-16 h-16 bg-slate-900 border border-cyan-900 grid grid-cols-8 grid-rows-8 gap-0 p-0.5 z-10 relative">
            {pageData.map((bit, i) => (
               <div key={i} className={`w-full h-full ${bit ? 'bg-cyan-400' : 'bg-transparent'}`}></div>
            ))}
            <div className="absolute -top-4 left-0 text-[8px] text-slate-500 font-mono">1Mb PAGE</div>
         </div>

         {/* The Crystal */}
         <div className="w-16 h-20 bg-cyan-900/40 border border-cyan-500/50 rounded flex items-center justify-center relative shadow-[0_0_20px_rgba(34,211,238,0.2)]">
            {/* Interference Pattern representation */}
            <div className="w-10 h-14 border border-cyan-400/30 rounded-sm bg-[repeating-linear-gradient(45deg,transparent,transparent_2px,rgba(34,211,238,0.2)_2px,rgba(34,211,238,0.2)_4px)]"></div>
            <div className="absolute -bottom-4 text-[8px] text-cyan-400 font-mono">LiNbO3</div>
         </div>

      </div>
      
      <div className="space-y-2 mb-4">
         <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400">Archival Progress</span>
            <span className="font-bold font-mono text-emerald-400">{writeProgress}%</span>
         </div>
         {/* Progress Bar */}
         <div className="w-full h-1.5 bg-slate-800 rounded relative overflow-hidden">
            <div className="absolute top-0 bottom-0 left-0 bg-emerald-500" style={{ width: `${writeProgress}%` }}></div>
         </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Throughput: <span className="text-white">120 MB/s</span></span>
         <span>Lifespan: <span className="text-cyan-400">100+ Years</span></span>
      </div>
    </div>
  );
};
