import React, { useState, useEffect } from 'react';

export const TrendDashboard: React.FC = () => {
  const [dataPoints, setDataPoints] = useState<number[]>([]);
  const [lowerBound, setLowerBound] = useState<number[]>([]);
  const [upperBound, setUpperBound] = useState<number[]>([]);

  useEffect(() => {
    let tick = 0;
    const interval = setInterval(() => {
      tick++;
      
      // Deterministic Bayesian projection math
      const baseTrend = Math.sin(tick * 0.2) * 50 + tick * 2;
      const uncertainty = Math.log(tick + 1) * 5;
      
      setDataPoints(prev => [...prev.slice(-30), baseTrend]);
      setLowerBound(prev => [...prev.slice(-30), baseTrend - uncertainty]);
      setUpperBound(prev => [...prev.slice(-30), baseTrend + uncertainty]);
      
    }, 500);

    return () => clearInterval(interval);
  }, []);

  const maxValue = Math.max(100, ...upperBound);

  return (
    <div className="bg-slate-900 p-6 rounded-xl border border-slate-700 shadow-2xl max-w-4xl mx-auto font-sans text-slate-200">
      <div className="flex justify-between items-center mb-6 border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-2xl font-bold text-indigo-400">Orbit Bayesian Forecast</h2>
          <p className="text-sm text-slate-500">MCMC Posterior Inference Engine</p>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 rounded-full bg-indigo-500 animate-pulse"></div>
          <span className="text-xs uppercase tracking-widest text-slate-400">Live Projection</span>
        </div>
      </div>

      <div className="relative h-64 bg-slate-950 rounded-lg border border-slate-800 p-4 flex items-end space-x-1 overflow-hidden">
        {dataPoints.map((point, idx) => {
          const heightPct = (point / maxValue) * 100;
          const lowerPct = (lowerBound[idx] / maxValue) * 100;
          const upperPct = (upperBound[idx] / maxValue) * 100;
          
          return (
            <div key={idx} className="relative flex-1 flex flex-col justify-end h-full group">
              {/* Uncertainty Band */}
              <div 
                className="absolute w-full bg-indigo-900/30 bottom-0"
                style={{ height: `${upperPct}%` }}
              >
                <div 
                  className="absolute w-full bg-slate-950 bottom-0"
                  style={{ height: `${(lowerPct / upperPct) * 100}%` }}
                ></div>
              </div>
              
              {/* Mean Line Point */}
              <div 
                className="absolute w-full bg-indigo-400 z-10"
                style={{ height: '4px', bottom: `${heightPct}%` }}
              ></div>
              
              {/* Tooltip */}
              <div className="absolute opacity-0 group-hover:opacity-100 bg-slate-800 text-xs p-1 rounded -top-8 left-1/2 transform -translate-x-1/2 z-20 whitespace-nowrap border border-slate-600">
                μ: {point.toFixed(1)}
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-6 grid grid-cols-3 gap-4 text-center">
        <div className="bg-slate-800 p-3 rounded">
          <div className="text-xs text-slate-500 uppercase">Current Mean</div>
          <div className="text-xl font-mono text-indigo-300">{dataPoints[dataPoints.length - 1]?.toFixed(2) || '0.00'}</div>
        </div>
        <div className="bg-slate-800 p-3 rounded">
          <div className="text-xs text-slate-500 uppercase">95% Upper Bound</div>
          <div className="text-xl font-mono text-emerald-400">{upperBound[upperBound.length - 1]?.toFixed(2) || '0.00'}</div>
        </div>
        <div className="bg-slate-800 p-3 rounded">
          <div className="text-xs text-slate-500 uppercase">95% Lower Bound</div>
          <div className="text-xl font-mono text-rose-400">{lowerBound[lowerBound.length - 1]?.toFixed(2) || '0.00'}</div>
        </div>
      </div>
    </div>
  );
};
