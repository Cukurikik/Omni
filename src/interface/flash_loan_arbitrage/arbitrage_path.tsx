import React, { useState, useEffect } from 'react';

export const ArbitragePath: React.FC = () => {
  const [activeNode, setActiveNode] = useState(0);
  const [profit, setProfit] = useState(0);

  useEffect(() => {
    // Simulate flash loan execution sequence
    const sequence = setInterval(() => {
      setActiveNode(prev => {
         const next = prev + 1;
         if (next === 4) { // Cycle complete
            setProfit(p => p + 1.2); // Add $1.2k profit
            setTimeout(() => setActiveNode(0), 1500); // Pause before next opp
            return 4;
         }
         return next > 4 ? 4 : next;
      });
    }, 400);

    return () => clearInterval(sequence);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-green-400">Flash Arbitrage</h2>
          <p className="text-xs text-slate-400">Bellman-Ford Negative Cycle</p>
        </div>
        <div className="text-[10px] font-mono bg-green-900/30 text-green-400 border border-green-800 px-2 py-1 rounded">
          Profit: +${profit.toFixed(1)}k
        </div>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 relative h-[180px] mb-4 flex items-center justify-center">
         
         <svg width="200" height="150" className="absolute z-0">
            {/* Triangular Path Lines */}
            <line x1="100" y1="20" x2="160" y2="120" stroke={activeNode >= 1 ? "#22c55e" : "#334155"} strokeWidth="2" strokeDasharray="4 4" className={activeNode === 1 ? "animate-pulse" : ""} />
            <line x1="160" y1="120" x2="40" y2="120" stroke={activeNode >= 2 ? "#22c55e" : "#334155"} strokeWidth="2" strokeDasharray="4 4" className={activeNode === 2 ? "animate-pulse" : ""} />
            <line x1="40" y1="120" x2="100" y2="20" stroke={activeNode >= 3 ? "#22c55e" : "#334155"} strokeWidth="2" strokeDasharray="4 4" className={activeNode === 3 ? "animate-pulse" : ""} />
         </svg>

         {/* Nodes */}
         <div className={`absolute top-2 w-12 h-12 rounded-full border-2 flex items-center justify-center z-10 transition-colors ${activeNode >= 0 ? 'bg-slate-800 border-green-500' : 'bg-slate-900 border-slate-600'}`}>
            <span className="text-[10px] font-bold text-white">ETH</span>
         </div>
         
         <div className={`absolute bottom-2 right-4 w-12 h-12 rounded-full border-2 flex items-center justify-center z-10 transition-colors ${activeNode >= 1 ? 'bg-slate-800 border-green-500' : 'bg-slate-900 border-slate-600'}`}>
            <span className="text-[10px] font-bold text-yellow-400">DAI</span>
         </div>

         <div className={`absolute bottom-2 left-4 w-12 h-12 rounded-full border-2 flex items-center justify-center z-10 transition-colors ${activeNode >= 2 ? 'bg-slate-800 border-green-500' : 'bg-slate-900 border-slate-600'}`}>
            <span className="text-[10px] font-bold text-teal-400">MKR</span>
         </div>
         
      </div>
      
      <div className="flex flex-col space-y-1 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <div className="flex justify-between"><span>Flash Loan Size:</span> <span className="text-white">10,000 ETH ($30M)</span></div>
         <div className="flex justify-between"><span>EVM Gas Cost:</span> <span className="text-red-400">-$125.00</span></div>
         <div className="flex justify-between border-t border-slate-700 pt-1 mt-1"><span>Net EV:</span> <span className="text-green-400 font-bold">Positive (Execute)</span></div>
      </div>
    </div>
  );
};
