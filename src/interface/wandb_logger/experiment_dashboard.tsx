import React, { useState, useEffect } from 'react';

export const ExperimentDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<{step: number, loss: number, acc: number}[]>([]);

  useEffect(() => {
    let step = 0;
    const interval = setInterval(() => {
      step++;
      
      // Deterministic learning curve simulation
      const loss = 2.0 * Math.exp(-step * 0.1) + (Math.sin(step) * 0.1) + 0.1;
      const acc = 1.0 - Math.exp(-step * 0.15) + (Math.cos(step) * 0.05);

      setMetrics(prev => {
        const next = [...prev, { step, loss, acc }];
        return next.length > 30 ? next.slice(1) : next;
      });

      if (step >= 100) clearInterval(interval);
    }, 200);

    return () => clearInterval(interval);
  }, []);

  const renderChart = (data: number[], color: string, label: string) => {
    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = max - min || 1;

    return (
      <div className="mb-6">
        <h3 className={`text-xs font-bold mb-2 ${color}`}>{label}</h3>
        <div className="h-24 bg-slate-950 border border-slate-800 rounded flex items-end gap-px p-1 overflow-hidden relative">
          {data.map((val, i) => {
            const pct = ((val - min) / range) * 100;
            return (
              <div 
                key={i}
                className={`flex-1 ${color.replace('text-', 'bg-')} transition-all duration-300 opacity-80 hover:opacity-100`}
                style={{ height: `${Math.max(1, pct)}%` }}
              />
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-2xl max-w-lg mx-auto font-sans">
      <div className="flex justify-between items-end mb-6 border-b border-slate-700 pb-4">
        <div>
          <h2 className="text-xl font-bold text-yellow-500">W&B Dashboard</h2>
          <p className="text-xs text-slate-400">Live Experiment Telemetry</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
          <span className="text-xs font-bold text-green-500">SYNCING</span>
        </div>
      </div>

      {metrics.length > 0 ? (
        <>
          {renderChart(metrics.map(m => m.loss), 'text-rose-500', 'Training Loss')}
          {renderChart(metrics.map(m => m.acc), 'text-emerald-500', 'Validation Accuracy')}
        </>
      ) : (
        <div className="text-slate-500 text-sm text-center py-10">Awaiting telemetry data...</div>
      )}
    </div>
  );
};
