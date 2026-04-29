import React, { useState, useEffect } from 'react';

export const MempoolViz: React.FC = () => {
  const [transactions, setTransactions] = useState<{id: number, value: number, isTarget: boolean}[]>([]);

  useEffect(() => {
    const interval = setInterval(() => {
      setTransactions(prev => {
         const next = [...prev];
         if (next.length > 20) next.shift(); // Keep UI clean
         
         // Randomly generate a "Target" whale transaction vulnerable to MEV
         const isTarget = Math.random() > 0.9;
         const value = isTarget ? Math.random() * 500 + 100 : Math.random() * 5;
         
         next.push({ id: Date.now(), value, isTarget });
         return next;
      });
    }, 200); // 5 tx/sec UI update

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-yellow-500">Mempool Sniper</h2>
          <p className="text-xs text-slate-400">MEV Dark Forest Monitor</p>
        </div>
        <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_#10b981] animate-pulse"></div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] overflow-hidden relative">
         {/* Particles representing pending transactions */}
         {transactions.map((tx) => (
            <div 
               key={tx.id}
               className={`absolute rounded-full transition-all duration-[2000ms] ease-linear
                  ${tx.isTarget ? 'bg-yellow-500 shadow-[0_0_15px_#eab308] border-2 border-white z-10' : 'bg-slate-600'}
               `}
               style={{
                  width: `${Math.max(4, Math.log10(tx.value) * 6)}px`,
                  height: `${Math.max(4, Math.log10(tx.value) * 6)}px`,
                  left: `${(tx.id % 100)}%`,
                  top: '110%',
                  transform: 'translateY(-300px)' // Move upwards to simulate flowing through mempool
               }}
            >
               {tx.isTarget && (
                  <div className="absolute top-4 left-4 text-[10px] font-mono text-yellow-400 bg-slate-900/80 px-1 rounded whitespace-nowrap">
                     TARGET: {tx.value.toFixed(1)} ETH
                  </div>
               )}
            </div>
         ))}
      </div>
      
      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Node: <span className="text-white">devp2p Raw Socket</span></span>
         <span>Latency: <span className="text-emerald-400">1.2 ms</span></span>
         <span className="col-span-2">Base Fee: <span className="text-sky-400 font-bold">14.2 Gwei</span></span>
      </div>
    </div>
  );
};
