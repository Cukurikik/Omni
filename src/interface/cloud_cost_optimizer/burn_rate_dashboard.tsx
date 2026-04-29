import React, { useState, useEffect } from 'react';

export const BurnRateDashboard: React.FC = () => {
  const [spend, setSpend] = useState(45200); // Current spend
  const budget = 50000;

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate real-time cloud burn (approx $5-10 per tick across a massive enterprise)
      setSpend(prev => prev + (Math.random() * 5 + 5));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const projected = spend * 1.15; // Simple projection to end of month
  const isAlert = projected > budget;
  const percentUsed = (spend / budget) * 100;

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-emerald-500">FinOps Center</h2>
          <p className="text-xs text-slate-400">Multi-Cloud Burn Rate</p>
        </div>
        {isAlert && (
          <div className="px-2 py-1 bg-red-900/50 text-red-400 text-[10px] font-mono rounded border border-red-800 animate-pulse">
            BUDGET EXCEEDED
          </div>
        )}
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 mb-4 flex justify-between items-center">
         <div>
            <div className="text-[10px] uppercase font-bold text-slate-500 mb-1">Current Spend</div>
            <div className="text-3xl font-mono text-white">${spend.toLocaleString('en-US', {maximumFractionDigits: 0})}</div>
         </div>
         <div className="h-10 w-px bg-slate-700"></div>
         <div className="text-right">
            <div className="text-[10px] uppercase font-bold text-slate-500 mb-1">Projected</div>
            <div className={`text-2xl font-mono ${isAlert ? 'text-red-500 font-bold' : 'text-slate-400'}`}>
               ${projected.toLocaleString('en-US', {maximumFractionDigits: 0})}
            </div>
         </div>
      </div>

      <div className="space-y-1 mb-4">
         <div className="flex justify-between text-xs font-mono mb-1">
            <span className="text-slate-400">Monthly Budget Usage</span>
            <span className="text-emerald-400">{percentUsed.toFixed(1)}%</span>
         </div>
         <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden relative">
            <div 
              className={`absolute top-0 bottom-0 left-0 transition-all duration-300 ${isAlert ? 'bg-red-500' : 'bg-emerald-500'}`}
              style={{ width: `${Math.min(100, percentUsed)}%` }}
            ></div>
         </div>
      </div>
      
      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <div className="flex items-center gap-1"><span className="text-orange-400 font-bold">AWS:</span> $28k</div>
         <div className="flex items-center gap-1"><span className="text-blue-400 font-bold">GCP:</span> $17k</div>
         <span className="col-span-2 text-xs border-t border-slate-700 pt-1 mt-1">
            Wasted Compute Found: <span className="text-emerald-400 font-bold">$1,240 (Idle EC2s)</span>
         </span>
      </div>
    </div>
  );
};
