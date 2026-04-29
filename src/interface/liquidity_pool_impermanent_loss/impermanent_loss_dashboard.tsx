import React, { useState, useEffect } from 'react';

export const ImpermanentLossDashboard: React.FC = () => {
  const [priceChange, setPriceChange] = useState(1.0); // Ratio (1.0 = no change)
  const baseApy = 25.0; // 25% APY from trading fees + farming

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate extreme crypto volatility
      setPriceChange(prev => {
         const drift = (Math.random() - 0.45) * 0.05; // Slight upward bias
         return Math.max(0.1, prev + drift);
      });
    }, 500);
    return () => clearInterval(interval);
  }, []);

  // IL = 2 * sqrt(k) / (1 + k) - 1
  const calculateIL = (k: number) => {
     return Math.abs((2 * Math.sqrt(k)) / (1 + k) - 1) * 100;
  };

  const ilPercent = calculateIL(priceChange);
  const netReturn = baseApy - ilPercent;
  const isLoss = netReturn < 0;

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-indigo-400">Yield Farming</h2>
          <p className="text-xs text-slate-400">Impermanent Loss vs APY</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-mono border ${isLoss ? 'bg-red-900/50 text-red-400 border-red-800 animate-pulse' : 'bg-emerald-900/30 text-emerald-400 border-emerald-800'}`}>
          {isLoss ? 'NET NEGATIVE' : 'PROFITABLE'}
        </div>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 mb-4 text-center">
         <div className="text-[10px] uppercase font-bold text-slate-500 mb-1">Asset Price Change Ratio</div>
         <div className="text-3xl font-mono font-bold text-white mb-2">
            {priceChange.toFixed(2)}x
         </div>
         
         {/* Net Yield Gauge */}
         <div className="w-full h-4 bg-slate-800 rounded overflow-hidden relative">
            <div 
               className={`absolute top-0 bottom-0 left-0 transition-all duration-300 ${isLoss ? 'bg-red-500' : 'bg-emerald-500'}`}
               style={{ width: `${Math.min(100, Math.max(0, 50 + (netReturn * 2)))}%` }}
            ></div>
            <div className="absolute top-0 bottom-0 left-1/2 w-px bg-white z-10"></div>
         </div>
      </div>
      
      <div className="space-y-2 mb-4">
         <div className="w-full bg-emerald-900/20 border border-emerald-800/50 p-2 rounded flex justify-between items-center text-xs font-mono">
            <span className="text-emerald-400">Farming APY Rewards</span>
            <span className="text-emerald-400 font-bold">+{baseApy.toFixed(2)}%</span>
         </div>
         <div className="w-full bg-red-900/20 border border-red-800/50 p-2 rounded flex justify-between items-center text-xs font-mono">
            <span className="text-red-400">Impermanent Loss (IL)</span>
            <span className="text-red-400 font-bold">-{ilPercent.toFixed(2)}%</span>
         </div>
      </div>

      <div className="flex justify-between items-center text-[12px] font-mono font-bold bg-slate-800 p-2 rounded">
         <span>Total Net Return:</span>
         <span className={isLoss ? 'text-red-400' : 'text-emerald-400'}>
            {netReturn > 0 ? '+' : ''}{netReturn.toFixed(2)}%
         </span>
      </div>
    </div>
  );
};
