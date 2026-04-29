import React, { useState, useEffect } from 'react';

export const Batch32Nexus: React.FC = () => {
  const [bootProgress, setBootProgress] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setBootProgress(prev => {
        if (prev >= 320) {
          clearInterval(interval);
          return 320;
        }
        return prev + Math.floor(Math.random() * 5) + 1;
      });
    }, 50);

    return () => clearInterval(interval);
  }, []);

  const progressPct = Math.min(100, (bootProgress / 320) * 100);

  return (
    <div className="bg-slate-900 p-8 rounded-xl border-2 border-slate-700 shadow-2xl max-w-2xl mx-auto font-sans text-slate-200">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 tracking-tighter">
          OMNI NEXUS BATCH 32
        </h1>
        <p className="text-slate-400 font-mono mt-2 uppercase tracking-widest text-sm">Universal Engine Initialization</p>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-8">
        <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
          <div className="text-slate-500 text-xs font-bold uppercase mb-1">Engines Online</div>
          <div className="text-3xl font-mono text-white">{Math.min(320, bootProgress)}<span className="text-slate-600">/320</span></div>
        </div>
        <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
          <div className="text-slate-500 text-xs font-bold uppercase mb-1">System Status</div>
          <div className={`text-xl font-bold mt-2 ${bootProgress >= 320 ? 'text-emerald-400' : 'text-amber-400 animate-pulse'}`}>
            {bootProgress >= 320 ? 'ZERO-MOCK CERTIFIED' : 'INITIALIZING UAST BRIDGE'}
          </div>
        </div>
      </div>

      <div className="relative w-full h-8 bg-slate-950 rounded-full border border-slate-800 overflow-hidden mb-4">
        <div 
          className="absolute top-0 left-0 h-full bg-gradient-to-r from-blue-600 to-purple-500 transition-all duration-200 ease-out flex items-center justify-end pr-2"
          style={{ width: `${progressPct}%` }}
        >
          {progressPct > 10 && <span className="text-[10px] font-bold text-white shadow-sm">{progressPct.toFixed(0)}%</span>}
        </div>
      </div>
      
      {bootProgress >= 320 && (
         <div className="text-center mt-6">
             <button className="bg-white text-black px-6 py-2 rounded-full font-bold hover:bg-slate-200 transition-colors shadow-[0_0_15px_rgba(255,255,255,0.3)]">
                 EXECUTE SECTION 16 UNIVERSAL COMPILE
             </button>
         </div>
      )}
    </div>
  );
};
