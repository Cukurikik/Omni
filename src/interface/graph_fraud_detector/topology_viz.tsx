import React, { useState, useEffect } from 'react';

export const TopologyViz: React.FC = () => {
  const [nodes, setNodes] = useState<{id: number, score: number}[]>(
    Array(9).fill(0).map((_, i) => ({ id: i, score: Math.random() }))
  );

  useEffect(() => {
    const interval = setInterval(() => {
      setNodes(prev => prev.map(n => {
        // GNN score propagates
        let newScore = n.score + (Math.random() - 0.5) * 0.2;
        newScore = Math.max(0, Math.min(1, newScore));
        return { ...n, score: newScore };
      }));
    }, 1500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 border-b border-slate-700 pb-2">
        <h2 className="text-xl font-bold text-rose-500">Graph Fraud AI</h2>
        <p className="text-xs text-slate-400">GNN Anomaly Propagation</p>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-4 place-items-center bg-slate-950 p-6 rounded border border-slate-800 relative">
        {/* Draw fake edges */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-20">
           <svg width="100%" height="100%">
             <line x1="16%" y1="16%" x2="50%" y2="50%" stroke="#fff" strokeWidth="2" />
             <line x1="84%" y1="16%" x2="50%" y2="50%" stroke="#fff" strokeWidth="2" />
             <line x1="50%" y1="84%" x2="50%" y2="50%" stroke="#fff" strokeWidth="2" />
           </svg>
        </div>

        {nodes.map(n => {
          const isFraud = n.score > 0.8;
          return (
            <div key={n.id} className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-xs z-10 transition-colors duration-500
              ${isFraud ? 'bg-rose-500 text-white shadow-[0_0_15px_#f43f5e]' : 'bg-slate-800 text-slate-400 border border-slate-700'}
            `}>
               {n.score.toFixed(2)}
            </div>
          )
        })}
      </div>

      <div className="text-[10px] text-slate-500 text-center uppercase tracking-widest font-bold">
        Message Passing Depth: l=2
      </div>
    </div>
  );
};
