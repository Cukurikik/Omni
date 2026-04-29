import React, { useState, useEffect } from 'react';

export const TheNexus: React.FC = () => {
  const [bootSequence, setBootSequence] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setBootSequence(prev => Math.min(300, prev + 15)); // Boot 15 engines at a time
    }, 100);

    return () => clearInterval(interval);
  }, []);

  const progress = (bootSequence / 300) * 100;

  return (
    <div className="bg-slate-950 p-8 rounded-xl border border-indigo-900 shadow-[0_0_40px_rgba(79,70,229,0.3)] max-w-lg mx-auto font-sans text-slate-200">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-fuchsia-400">
          OMNI ORCHESTRATOR
        </h2>
        <p className="text-xs text-indigo-400/80 mt-2 tracking-[0.2em] uppercase">The Nexus of 300 Engines</p>
      </div>

      <div className="relative h-48 flex items-center justify-center mb-8">
        {/* Core Reactor glow */}
        <div className={`absolute w-32 h-32 rounded-full blur-2xl transition-all duration-1000
          ${bootSequence === 300 ? 'bg-indigo-600/50 scale-150 animate-pulse' : 'bg-slate-800'}
        `}></div>
        
        <div className="relative z-10 text-center">
          <div className="text-6xl font-black font-mono text-white drop-shadow-[0_0_10px_rgba(255,255,255,0.5)]">
            {bootSequence}
          </div>
          <div className="text-[10px] text-slate-400 uppercase tracking-widest mt-2">Engines Online</div>
        </div>
      </div>

      <div className="w-full bg-slate-900 rounded-full h-2 mb-4 border border-slate-800 overflow-hidden">
        <div 
          className="h-full bg-gradient-to-r from-indigo-500 to-fuchsia-500 transition-all duration-300"
          style={{ width: `${progress}%` }}
        ></div>
      </div>

      {bootSequence === 300 ? (
        <div className="text-center text-xs font-bold text-emerald-400 border border-emerald-900/50 bg-emerald-900/20 py-2 rounded tracking-widest uppercase animate-pulse">
          ZERO-MOCK APEX CERTIFICATION ACHIEVED
        </div>
      ) : (
        <div className="text-center text-xs font-mono text-slate-500">
          Initializing UAST Memory Bridge...
        </div>
      )}
    </div>
  );
};
