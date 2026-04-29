import React, { useEffect, useState } from 'react';

interface MetricPoint {
  epoch: number;
  accuracy: number;
  loss: number;
}

export const MetricsDashboard: React.FC = () => {
  const [data, setData] = useState<MetricPoint[]>([]);

  useEffect(() => {
    let animationFrameId: number;
    let epochCounter = 0;

    const renderLoop = () => {
      epochCounter += 1;
      if (epochCounter > 100) return; // Stop after 100 epochs

      setData(prev => {
        const newData = [...prev];
        // Deterministic logarithmic training curve
        const acc = 0.95 - (0.5 * Math.exp(-epochCounter / 20));
        const loss = 1.0 * Math.exp(-epochCounter / 15);
        
        newData.push({ epoch: epochCounter, accuracy: acc, loss: loss });
        if (newData.length > 20) newData.shift();
        return newData;
      });

      // Slow down the update rate
      setTimeout(() => {
        animationFrameId = requestAnimationFrame(renderLoop);
      }, 100);
    };

    renderLoop();

    return () => cancelAnimationFrame(animationFrameId);
  }, []);

  return (
    <div className="p-6 bg-slate-900 text-white font-mono rounded-lg shadow-xl">
      <h2 className="text-xl font-bold mb-4 text-blue-400">TorchMetrics Live Dashboard</h2>
      
      <div className="flex gap-4 mb-4">
        <div className="p-4 bg-slate-800 rounded">
          <p className="text-sm text-gray-400">Current Accuracy</p>
          <p className="text-2xl font-bold text-green-400">
            {data.length > 0 ? (data[data.length - 1].accuracy * 100).toFixed(2) + '%' : '0.00%'}
          </p>
        </div>
        <div className="p-4 bg-slate-800 rounded">
          <p className="text-sm text-gray-400">Current Loss</p>
          <p className="text-2xl font-bold text-red-400">
            {data.length > 0 ? data[data.length - 1].loss.toFixed(4) : '0.0000'}
          </p>
        </div>
      </div>

      <div className="h-40 bg-black relative border-l border-b border-slate-700">
        {data.map((pt, i) => (
          <div 
            key={pt.epoch}
            className="absolute bottom-0 w-2 bg-blue-500"
            style={{ 
              left: `${(i / 20) * 100}%`, 
              height: `${pt.accuracy * 100}%`,
              transition: 'all 0.1s'
            }}
          />
        ))}
      </div>
    </div>
  );
};
