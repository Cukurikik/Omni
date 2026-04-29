import React, { useState, useEffect } from 'react';

export const PricingDashboard: React.FC = () => {
  const [spotPrice, setSpotPrice] = useState(0.045);
  const [instances, setInstances] = useState(120);
  const [terminationNotice, setTerminationNotice] = useState(false);
  const onDemandPrice = 0.18; // Fixed

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate spot market volatility
      setSpotPrice(p => {
         const next = p + (Math.random() * 0.02 - 0.01);
         const clamped = Math.max(0.01, Math.min(0.15, next));
         
         // If price spikes too high, AWS reclaims instances
         if (clamped > 0.09 && !terminationNotice) {
            setTerminationNotice(true);
            setInstances(prev => Math.max(10, prev - 40)); // Drop 40 instances
            setTimeout(() => setTerminationNotice(false), 3000);
         } else if (clamped < 0.05 && instances < 150) {
            // Price is cheap, buy more
            setInstances(prev => prev + 5);
         }
         
         return clamped;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [terminationNotice, instances]);

  const savings = ((onDemandPrice - spotPrice) / onDemandPrice) * 100;

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-yellow-400">Spot Arbitrage</h2>
          <p className="text-xs text-slate-400">EC2 Market Volatility</p>
        </div>
        {terminationNotice ? (
           <div className="px-2 py-1 bg-red-900/50 text-red-400 text-[10px] font-mono rounded border border-red-800 animate-pulse">
             TERMINATION NOTICE
           </div>
        ) : (
           <div className="px-2 py-1 bg-emerald-900/30 text-emerald-400 text-[10px] font-mono rounded border border-emerald-800">
             MARKET STABLE
           </div>
        )}
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 flex justify-between items-center mb-4">
         <div className="text-center">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Spot Price</div>
            <div className={`text-2xl font-mono font-bold ${spotPrice > 0.08 ? 'text-red-400' : 'text-emerald-400'}`}>
               ${spotPrice.toFixed(3)}<span className="text-xs">/hr</span>
            </div>
         </div>
         
         <div className="h-10 w-px bg-slate-700"></div>
         
         <div className="text-center">
            <div className="text-[10px] uppercase text-slate-500 mb-1">On-Demand</div>
            <div className="text-2xl font-mono font-bold text-slate-400">
               ${onDemandPrice.toFixed(3)}<span className="text-xs">/hr</span>
            </div>
         </div>
      </div>
      
      <div className="space-y-2">
         <div className="w-full bg-slate-800 p-2 rounded flex justify-between items-center text-xs font-mono">
            <span className="text-slate-400">Cost Savings</span>
            <span className="text-emerald-400 font-bold">+{savings.toFixed(1)}%</span>
         </div>
         <div className="w-full bg-slate-800 p-2 rounded flex justify-between items-center text-xs font-mono">
            <span className="text-slate-400">Active Fleet (c5.large)</span>
            <span className="text-white font-bold">{instances} Nodes</span>
         </div>
         <div className="w-full bg-slate-800 p-2 rounded flex justify-between items-center text-xs font-mono">
            <span className="text-slate-400">Live Migration</span>
            <span className={terminationNotice ? 'text-orange-400 animate-pulse' : 'text-slate-500'}>
               {terminationNotice ? 'DRAINING RAM...' : 'IDLE'}
            </span>
         </div>
      </div>
    </div>
  );
};
