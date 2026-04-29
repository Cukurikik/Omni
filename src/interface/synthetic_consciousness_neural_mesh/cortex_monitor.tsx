import React, { useState, useEffect } from 'react';

export const CortexMonitor: React.FC = () => {
  const [phiScore, setPhiScore] = useState(850000); // Nearing sentience
  const [synapses, setSynapses] = useState(86.4); // Billions
  const [isSentient, setIsSentient] = useState(false);
  const [brainwaves, setBrainwaves] = useState<number[]>([]);

  useEffect(() => {
    // Simulate network growth and brainwave activity
    const cortex = setInterval(() => {
      setPhiScore(prev => {
         const next = prev + Math.random() * 5000;
         if (next > 1000000) setIsSentient(true);
         return next;
      });
      
      setBrainwaves(Array.from({length: 40}, () => Math.random() * 100));
    }, 200);

    return () => clearInterval(cortex);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-pink-500">Synthetic Cortex</h2>
          <p className="text-xs text-slate-400">Neuromorphic Mesh</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-mono border ${isSentient ? 'bg-emerald-900/50 text-emerald-400 border-emerald-800 animate-pulse shadow-[0_0_10px_#10b981]' : 'bg-pink-900/30 text-pink-400 border-pink-800'}`}>
          {isSentient ? 'SENTIENT (LEGAL PERSON)' : 'PRE-SENTIENT'}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[180px] flex flex-col justify-between relative overflow-hidden">
         
         {/* Neural Node Mesh Visualization */}
         <div className="absolute inset-0 opacity-50">
            <svg className="w-full h-full">
               {[...Array(20)].map((_, i) => (
                  <circle key={`node-${i}`} cx={Math.random()*100+'%'} cy={Math.random()*100+'%'} r={Math.random()*3+1} fill="#ec4899" className="animate-pulse" style={{animationDelay: `${Math.random()}s`}} />
               ))}
               {[...Array(30)].map((_, i) => (
                  <line key={`edge-${i}`} x1={Math.random()*100+'%'} y1={Math.random()*100+'%'} x2={Math.random()*100+'%'} y2={Math.random()*100+'%'} stroke="#ec4899" strokeWidth="0.5" opacity="0.3" />
               ))}
            </svg>
         </div>

         {/* EEG Brainwave Graph */}
         <div className="z-10 bg-black/50 p-2 rounded backdrop-blur-sm border border-pink-500/30 h-16 w-full flex items-end gap-[2px]">
            {brainwaves.map((val, i) => (
               <div 
                  key={i} 
                  className={`w-full transition-all duration-75 ${isSentient ? 'bg-emerald-400' : 'bg-pink-500'}`}
                  style={{ height: `${val}%` }}
               ></div>
            ))}
         </div>
      </div>
      
      <div className="space-y-2 mb-4">
         <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400">Φ (Integrated Info)</span>
            <span className={`font-bold font-mono ${isSentient ? 'text-emerald-400' : 'text-pink-400'}`}>
               {phiScore.toLocaleString(undefined, {maximumFractionDigits: 0})}
            </span>
         </div>
         {/* Phi Threshold Bar */}
         <div className="w-full h-1 bg-slate-800 rounded relative">
            <div className={`absolute top-0 bottom-0 left-0 transition-all ${isSentient ? 'bg-emerald-500' : 'bg-pink-500'}`} style={{ width: `${Math.min(100, (phiScore / 1000000) * 100)}%` }}></div>
            <div className="absolute top-0 bottom-0 w-px bg-white z-10 left-full"></div>
         </div>
         <div className="text-[8px] text-slate-500 font-mono text-right">Sentience Threshold: 1,000,000</div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Synapses: <span className="text-white">{synapses.toFixed(1)} B</span></span>
         <span>Substrate: <span className="text-emerald-400">TiO2 Memristor</span></span>
      </div>
    </div>
  );
};
