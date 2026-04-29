import React, { useState, useEffect } from 'react';

export const ConnectomeUi: React.FC = () => {
  const [learningPhase, setLearningPhase] = useState<'WAKE' | 'REM_SLEEP'>('WAKE');
  const [memoryStability, setMemoryStability] = useState(10);
  const [spikes, setSpikes] = useState<{id: number, x: number, y: number}[]>([]);

  useEffect(() => {
    // Neural activity simulation
    const brain = setInterval(() => {
       // Generate random action potentials (spikes)
       if (learningPhase === 'WAKE') {
          setSpikes(prev => [
             ...prev.slice(-15), // Keep last 15
             { id: Date.now(), x: Math.random() * 100, y: Math.random() * 100 }
          ]);
          // Memories degrade slightly while awake (forgetting curve)
          setMemoryStability(prev => Math.max(0, prev - 1));
       } else {
          // REM Sleep: Structured, synchronized bursts (memory consolidation)
          const isBurst = Math.random() > 0.7;
          if (isBurst) {
             const burstX = Math.random() * 100;
             const burstY = Math.random() * 100;
             setSpikes(Array.from({length: 5}, (_, i) => ({
                id: Date.now() + i,
                x: burstX + (Math.random() - 0.5) * 20,
                y: burstY + (Math.random() - 0.5) * 20
             })));
             // Memories consolidate during sleep
             setMemoryStability(prev => Math.min(100, prev + 5));
          } else {
             setSpikes([]);
          }
       }
    }, 200);

    return () => clearInterval(brain);
  }, [learningPhase]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-teal-400">Neuroplastic Mesh</h2>
          <p className="text-xs text-slate-400">Connectome Compiler</p>
        </div>
        <div className="flex gap-2">
           <button 
              onClick={() => setLearningPhase('WAKE')} 
              className={`px-2 py-1 text-[10px] font-mono rounded border ${learningPhase === 'WAKE' ? 'bg-teal-900/50 text-teal-400 border-teal-800 shadow-[0_0_8px_#2dd4bf]' : 'bg-slate-800 text-slate-400 border-slate-700'}`}
           >
              WAKE
           </button>
           <button 
              onClick={() => setLearningPhase('REM_SLEEP')} 
              className={`px-2 py-1 text-[10px] font-mono rounded border ${learningPhase === 'REM_SLEEP' ? 'bg-indigo-900/50 text-indigo-400 border-indigo-800 shadow-[0_0_8px_#818cf8] animate-pulse' : 'bg-slate-800 text-slate-400 border-slate-700'}`}
           >
              SLEEP
           </button>
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[180px] flex items-center justify-center relative overflow-hidden">
         
         {/* Background Synaptic Grid */}
         <div className="absolute inset-0 opacity-20">
            {[...Array(50)].map((_, i) => (
               <div key={i} className="absolute w-1 h-1 bg-teal-500 rounded-full" style={{ left: `${Math.random()*100}%`, top: `${Math.random()*100}%` }}></div>
            ))}
         </div>

         {/* Action Potential Spikes */}
         {spikes.map(s => (
            <div 
               key={s.id}
               className={`absolute w-16 h-16 -ml-8 -mt-8 rounded-full border-2 opacity-0 animate-[ping_0.5s_ease-out_forwards] ${learningPhase === 'WAKE' ? 'border-teal-400' : 'border-indigo-500'}`}
               style={{ left: `${s.x}%`, top: `${s.y}%` }}
            ></div>
         ))}
         
         {/* Core Memory Engram (Grows brighter as memory stabilizes) */}
         <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div 
               className="w-24 h-24 rounded-full bg-teal-500 blur-2xl transition-opacity duration-1000"
               style={{ opacity: memoryStability / 200 }}
            ></div>
         </div>
      </div>
      
      <div className="space-y-2 mb-4">
         <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400">Engram Stability (LTP)</span>
            <span className="font-bold font-mono text-white">{memoryStability}%</span>
         </div>
         {/* Stability Bar */}
         <div className="w-full h-2 bg-slate-800 rounded relative overflow-hidden border border-slate-700">
            <div className={`absolute top-0 bottom-0 left-0 transition-all duration-300 ${memoryStability > 80 ? 'bg-teal-500' : memoryStability > 40 ? 'bg-indigo-500' : 'bg-red-500'}`} style={{ width: `${memoryStability}%` }}></div>
         </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Plasticity: <span className="text-emerald-400">STDP Enabled</span></span>
         <span>Interface: <span className="text-emerald-400">Utah Array</span></span>
      </div>
    </div>
  );
};
