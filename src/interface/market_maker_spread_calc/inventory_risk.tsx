import React, { useState, useEffect } from 'react';

export const InventoryRisk: React.FC = () => {
  const [inventory, setInventory] = useState(0);
  const maxLimit = 1000;

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate market maker filling orders (random walk inventory drift)
      setInventory(prev => {
         // Drift upwards to simulate a market sell-off where we are buying
         const next = prev + (Math.random() * 50 - 15);
         return Math.max(-1000, Math.min(1000, next));
      });
    }, 400);
    return () => clearInterval(interval);
  }, []);

  const inventoryPercent = (Math.abs(inventory) / maxLimit) * 100;
  const isDanger = inventoryPercent > 80;

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-amber-500">Market Maker</h2>
          <p className="text-xs text-slate-400">Inventory Risk Limits</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-mono border ${isDanger ? 'bg-red-900/50 text-red-400 border-red-800 animate-pulse' : 'bg-emerald-900/30 text-emerald-400 border-emerald-800'}`}>
          {isDanger ? 'HALT QUOTING' : 'PROVIDING'}
        </div>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 mb-4 text-center">
         <div className="text-[10px] uppercase font-bold text-slate-500 mb-1">Current Net Inventory</div>
         <div className={`text-3xl font-mono font-bold ${inventory > 0 ? 'text-sky-400' : 'text-rose-400'}`}>
            {inventory > 0 ? '+' : ''}{inventory.toFixed(0)} <span className="text-sm">BTC</span>
         </div>
         
         {/* Inventory Gauge */}
         <div className="w-full h-3 bg-slate-800 rounded-full overflow-hidden relative mt-4">
            {/* Center line */}
            <div className="absolute top-0 bottom-0 w-px bg-slate-400 z-10 left-1/2"></div>
            
            {/* Fill bar */}
            <div 
               className={`absolute top-0 bottom-0 transition-all duration-300 ${inventory > 0 ? 'bg-sky-500' : 'bg-rose-500'}`}
               style={{ 
                  left: inventory > 0 ? '50%' : `${50 - (inventoryPercent/2)}%`,
                  width: `${inventoryPercent/2}%` 
               }}
            ></div>
         </div>
         <div className="flex justify-between text-[8px] font-mono text-slate-500 mt-1">
            <span>-1000 (Short)</span>
            <span>0 (Flat)</span>
            <span>+1000 (Long)</span>
         </div>
      </div>
      
      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Model: <span className="text-white">Avellaneda-Stoikov</span></span>
         <span>Volatility: <span className="text-amber-400">High</span></span>
         <span className="col-span-2 text-slate-500">Spread: Widened to mitigate toxic flow</span>
      </div>
    </div>
  );
};
