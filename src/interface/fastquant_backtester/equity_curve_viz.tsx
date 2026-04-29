import React, { useState, useEffect } from 'react';

export const EquityCurveViz: React.FC = () => {
  const [equity, setEquity] = useState<number[]>([10000]);

  useEffect(() => {
    const interval = setInterval(() => {
      setEquity(prev => {
        if (prev.length > 30) return prev; // Stop simulation
        const last = prev[prev.length - 1];
        // Simulated ML Strategy returns with upward drift and volatility
        const dailyReturn = 1 + (Math.random() * 0.04 - 0.015);
        return [...prev, last * dailyReturn];
      });
    }, 200);

    return () => clearInterval(interval);
  }, []);

  const currentEquity = equity[equity.length - 1];
  const roi = ((currentEquity - 10000) / 10000) * 100;

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-green-400">FastQuant</h2>
          <p className="text-xs text-slate-400">ML Strategy Backtest</p>
        </div>
        <div className={`text-xl font-mono font-bold ${roi >= 0 ? 'text-green-500' : 'text-red-500'}`}>
          {roi >= 0 ? '+' : ''}{roi.toFixed(2)}%
        </div>
      </div>

      <div className="relative h-32 bg-slate-950 p-2 rounded border border-slate-800 flex items-end">
        <svg width="100%" height="100%" preserveAspectRatio="none">
          <polyline 
            fill="none" 
            stroke="#4ade80" 
            strokeWidth="2" 
            points={equity.map((val, i) => {
              const x = (i / 30) * 100;
              // Map 9000-15000 to 100-0 height
              const max = 15000;
              const min = 9000;
              const y = 100 - ((val - min) / (max - min)) * 100;
              return `${x},${y}`;
            }).join(' ')}
          />
        </svg>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-2 text-xs font-mono">
        <div className="bg-slate-800 p-2 rounded border border-slate-700">
          <div className="text-slate-500">Sharpe Ratio</div>
          <div className="text-white">2.14</div>
        </div>
        <div className="bg-slate-800 p-2 rounded border border-slate-700">
          <div className="text-slate-500">Max Drawdown</div>
          <div className="text-red-400">-8.4%</div>
        </div>
      </div>
    </div>
  );
};
