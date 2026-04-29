import React, { useState, useEffect } from 'react';

export const BciDashboard: React.FC = () => {
  const [spikes, setSpikes] = useState<{x: number, y: number, cluster: number}[]>([]);
  const [confidence, setConfidence] = useState(0.4);

  useEffect(() => {
    // Simulate real-time PCA Spike Sorting (Clustering)
    const interval = setInterval(() => {
      setSpikes(prev => {
         const next = [...prev];
         if (next.length > 50) next.shift(); // Keep UI clean
         
         // Randomly generate a spike belonging to Neuron A (cluster 1) or Neuron B (cluster 2)
         const cluster = Math.random() > 0.5 ? 1 : 2;
         const baseX = cluster === 1 ? 30 : 70;
         const baseY = cluster === 1 ? 70 : 30;
         
         const x = baseX + (Math.random() - 0.5) * 15;
         const y = baseY + (Math.random() - 0.5) * 15;
         
         next.push({ x, y, cluster });
         return next;
      });

      // Fluctuate decoding confidence
      setConfidence(prev => Math.max(0.1, Math.min(0.99, prev + (Math.random() - 0.5) * 0.1)));

    }, 50);

    return () => clearInterval(interval);
  }, []);

  const intent = confidence > 0.85 ? 'MOVE_ARM_RIGHT' : 'IDLE';

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-fuchsia-400">Neural Interface</h2>
          <p className="text-xs text-slate-400">PCA Spike Sorting</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-mono border ${intent === 'IDLE' ? 'bg-slate-800 text-slate-400 border-slate-700' : 'bg-emerald-900/50 text-emerald-400 border-emerald-800 animate-pulse'}`}>
          {intent}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[160px] relative overflow-hidden">
         <div className="absolute top-2 left-2 text-[10px] text-slate-500 font-mono">PC2</div>
         <div className="absolute bottom-2 right-2 text-[10px] text-slate-500 font-mono">PC1</div>
         
         {/* Scatter Plot of PCA isolated action potentials */}
         {spikes.map((s, i) => (
            <div 
               key={i}
               className={`absolute w-1.5 h-1.5 rounded-full opacity-80 ${s.cluster === 1 ? 'bg-fuchsia-400 shadow-[0_0_5px_#e879f9]' : 'bg-sky-400 shadow-[0_0_5px_#38bdf8]'}`}
               style={{ left: `${s.x}%`, top: `${s.y}%` }}
            ></div>
         ))}
      </div>
      
      <div className="space-y-2 mb-4">
         <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400">Decoding Confidence</span>
            <span className={`font-bold font-mono ${confidence > 0.85 ? 'text-emerald-400' : 'text-slate-300'}`}>{(confidence * 100).toFixed(1)}%</span>
         </div>
         {/* Confidence Bar */}
         <div className="w-full h-1.5 bg-slate-800 rounded relative overflow-hidden">
            <div className={`absolute top-0 bottom-0 left-0 transition-all duration-75 ${confidence > 0.85 ? 'bg-emerald-500' : 'bg-fuchsia-500'}`} style={{ width: `${confidence * 100}%` }}></div>
            <div className="absolute top-0 bottom-0 w-px bg-red-500 z-10" style={{ left: '85%' }}></div>
         </div>
         <div className="text-[8px] text-right text-slate-500 font-mono">Actuation Threshold: 85%</div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Channels: <span className="text-white">1024 (Utah)</span></span>
         <span>Sampling: <span className="text-sky-400">30 kHz</span></span>
      </div>
    </div>
  );
};
