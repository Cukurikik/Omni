import React, { useState, useEffect } from 'react';

export const SpreadViz: React.FC = () => {
  const [nodes, setNodes] = useState<boolean[]>(Array(64).fill(false));
  const [round, setRound] = useState(0);

  useEffect(() => {
    // Initial patient zero
    setNodes(prev => {
      const next = [...prev];
      next[32] = true; 
      return next;
    });

    const interval = setInterval(() => {
      setRound(r => r + 1);
      
      setNodes(prev => {
        const next = [...prev];
        const fanout = 2; // Each infected node contacts 2 random nodes
        
        const infectedIndices = prev.map((v, i) => v ? i : -1).filter(i => i !== -1);
        
        if (infectedIndices.length === 64) {
          // Fully saturated, reset for simulation loop
          setTimeout(() => {
            setRound(0);
            setNodes(Array(64).fill(false));
            setNodes(p => { const n = [...p]; n[32] = true; return n; });
          }, 2000);
          return next;
        }

        infectedIndices.forEach(() => {
          for(let f=0; f<fanout; f++) {
            const target = Math.floor(Math.random() * 64);
            next[target] = true; // Infect
          }
        });
        
        return next;
      });
    }, 600);

    return () => clearInterval(interval);
  }, []);

  const infectedCount = nodes.filter(Boolean).length;
  const pct = ((infectedCount / 64) * 100).toFixed(0);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 flex justify-between items-center border-b border-slate-700 pb-3">
        <div>
          <h2 className="text-xl font-bold text-lime-500">Gossip Protocol</h2>
          <p className="text-xs text-slate-400">Epidemic Broadcast Spread</p>
        </div>
        <div className="text-right">
           <div className="text-[10px] text-slate-400 font-bold uppercase tracking-wider mb-1">Round {round}</div>
           <div className="text-xl font-mono font-black text-lime-400">{pct}%</div>
        </div>
      </div>

      <div className="grid grid-cols-8 gap-1">
        {nodes.map((isInfected, i) => (
          <div key={i} className={`w-8 h-8 rounded-sm transition-colors duration-300 border border-slate-800
            ${isInfected ? 'bg-lime-500/80 shadow-[0_0_8px_#84cc16]' : 'bg-slate-800'}
          `}></div>
        ))}
      </div>
      
      <div className="text-[10px] text-slate-500 text-center mt-4 uppercase tracking-widest font-bold">
         O(log N) Convergence Guarantee
      </div>
    </div>
  );
};
