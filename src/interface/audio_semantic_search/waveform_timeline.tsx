import React, { useState, useEffect } from 'react';

export const WaveformTimeline: React.FC = () => {
  const [playhead, setPlayhead] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setPlayhead(prev => (prev > 100 ? 0 : prev + 1));
    }, 100);
    return () => clearInterval(interval);
  }, []);

  // Generate deterministic waveform bars
  const bars = Array.from({ length: 40 }).map((_, i) => {
     return 20 + Math.abs(Math.sin(i * 0.5) * 40) + Math.abs(Math.cos(i * 1.3) * 20);
  });

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-cyan-400">Audio Semantic Search</h2>
        <p className="text-xs text-slate-400">MFCC Vector Retrieval</p>
      </div>

      <div className="bg-slate-800 p-3 rounded mb-4 text-xs font-mono border border-slate-600 flex justify-between items-center">
         <span className="text-slate-300">"Find when they discussed the Q3 budget"</span>
         <span className="bg-cyan-900/50 text-cyan-400 px-2 py-1 rounded text-[10px]">Query</span>
      </div>

      <div className="bg-slate-950 rounded border border-slate-800 h-[100px] relative flex items-end justify-between px-2 pb-2">
         {/* Semantic Match Highlight */}
         <div className="absolute top-0 bottom-0 left-[60%] w-[15%] bg-cyan-500/20 border-l border-r border-cyan-500/50">
             <div className="absolute -top-2 left-1/2 transform -translate-x-1/2 bg-cyan-500 text-slate-900 text-[8px] font-bold px-1 rounded">MATCH</div>
         </div>

         {/* Audio Waveform */}
         {bars.map((h, i) => (
           <div 
             key={i} 
             className={`w-1.5 rounded-t transition-all ${i >= 24 && i <= 29 ? 'bg-cyan-400' : 'bg-slate-600'}`}
             style={{ height: `${h}%` }}
           ></div>
         ))}
         
         {/* Playhead */}
         <div 
           className="absolute top-0 bottom-0 w-px bg-rose-500 shadow-[0_0_5px_rgba(244,63,94,0.8)] z-10"
           style={{ left: `${playhead}%` }}
         >
             <div className="absolute -top-1 -left-1 w-2 h-2 rounded-full bg-rose-500"></div>
         </div>
      </div>
      
      <div className="mt-3 flex justify-between font-mono text-[10px] text-slate-500">
         <span>0:00</span>
         <span>Found at 0:42</span>
         <span>1:15</span>
      </div>
    </div>
  );
};
