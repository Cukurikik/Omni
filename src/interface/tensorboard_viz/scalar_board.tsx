import React, { useState, useEffect } from 'react';

export const ScalarBoard: React.FC = () => {
  const [metrics, setMetrics] = useState<{tag: string, data: {step: number, val: number}[]}[]>([
    { tag: 'loss/train', data: [] },
    { tag: 'accuracy/train', data: [] },
    { tag: 'learning_rate', data: [] }
  ]);

  useEffect(() => {
    let step = 0;
    const interval = setInterval(() => {
      step += 100;
      
      // Deterministic TensorBoard simulation curves
      const trainLoss = 2.5 * Math.exp(-step * 0.001) + (Math.sin(step * 0.05) * 0.1) + 0.2;
      const trainAcc = 1.0 - Math.exp(-step * 0.002) + (Math.cos(step * 0.05) * 0.02);
      const lr = 0.001 * Math.pow(0.9, Math.floor(step / 1000));

      setMetrics(prev => [
        { tag: 'loss/train', data: [...prev[0].data, { step, val: trainLoss }].slice(-50) },
        { tag: 'accuracy/train', data: [...prev[1].data, { step, val: trainAcc }].slice(-50) },
        { tag: 'learning_rate', data: [...prev[2].data, { step, val: lr }].slice(-50) }
      ]);

      if (step >= 5000) clearInterval(interval);
    }, 150);

    return () => clearInterval(interval);
  }, []);

  const renderChart = (tag: string, data: {step: number, val: number}[]) => {
    if (data.length === 0) return null;
    
    const min = Math.min(...data.map(d => d.val));
    const max = Math.max(...data.map(d => d.val));
    const range = max - min || 1;

    return (
      <div className="bg-white p-4 rounded shadow border border-slate-200">
        <h3 className="text-xs font-bold text-slate-700 mb-2">{tag}</h3>
        <div className="h-32 bg-slate-50 flex items-end relative overflow-hidden group">
          {/* Grid lines */}
          <div className="absolute inset-0 border-y border-slate-200 pointer-events-none opacity-50"></div>
          
          {/* Path rendering approximation using SVGs for smooth TensorBoard look */}
          <svg className="absolute inset-0 w-full h-full preserve-3d" preserveAspectRatio="none" viewBox="0 0 100 100">
            <polyline 
              fill="none" 
              stroke="#f97316" // Tensorboard Orange
              strokeWidth="2"
              points={data.map((d, i) => `${(i / Math.max(1, data.length - 1)) * 100},${100 - ((d.val - min) / range) * 100}`).join(' ')}
            />
          </svg>
        </div>
        <div className="flex justify-between text-[10px] text-slate-400 mt-1 font-mono">
          <span>{data[0]?.step || 0}</span>
          <span>{data[data.length-1]?.step || 0}</span>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-slate-100 p-6 rounded-lg border border-slate-300 shadow-xl max-w-3xl mx-auto font-sans">
      <div className="mb-6 border-b border-slate-300 pb-2">
        <h2 className="text-xl font-bold text-orange-600">TensorBoard</h2>
        <p className="text-xs text-slate-500">Scalar Visualizations</p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {metrics.map(m => (
          <div key={m.tag}>{renderChart(m.tag, m.data)}</div>
        ))}
      </div>
    </div>
  );
};
