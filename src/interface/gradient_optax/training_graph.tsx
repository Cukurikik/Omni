import React, { useEffect, useState } from 'react';

export const TrainingGraph: React.FC = () => {
  const [lossData, setLossData] = useState<number[]>([]);
  const [lr, setLr] = useState(0.1);

  useEffect(() => {
    let epoch = 0;
    const interval = setInterval(() => {
      epoch++;
      
      // Deterministic loss curve simulation
      // f(x) = e^(-0.05*x) + 0.1*sin(x)
      const currentLoss = Math.exp(-0.05 * epoch) + (0.1 * Math.sin(epoch)) + 0.05;
      
      setLossData(prev => [...prev.slice(-49), Number(currentLoss.toFixed(4))]);

      // Simulate LR decay
      if (epoch % 20 === 0) setLr(prev => prev * 0.5);

    }, 200);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="w-full max-w-3xl mx-auto p-6 bg-[#0d1117] text-white rounded-lg border border-[#30363d] shadow-xl font-sans">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-[#58a6ff]">Optax Training Dashboard</h2>
        <div className="text-sm">
          LR: <span className="text-[#3fb950] font-mono">{lr.toExponential(2)}</span>
        </div>
      </div>

      <div className="h-48 w-full bg-[#161b22] border border-[#30363d] rounded p-2 flex items-end space-x-1 overflow-hidden relative">
        {/* Y Axis Guides */}
        <div className="absolute left-2 top-2 text-xs text-gray-500">Loss</div>
        <div className="absolute left-0 top-0 w-full h-full flex flex-col justify-between pointer-events-none opacity-10">
          <div className="w-full border-t border-white"></div>
          <div className="w-full border-t border-white"></div>
          <div className="w-full border-t border-white"></div>
          <div className="w-full border-t border-white"></div>
        </div>

        {lossData.map((loss, idx) => (
          <div 
            key={idx} 
            className="w-full bg-[#58a6ff] transition-all duration-100 ease-linear rounded-t-sm"
            style={{ height: `${Math.min(100, Math.max(5, loss * 80))}%`, minWidth: '4px' }}
            title={`Epoch ${idx}: ${loss}`}
          ></div>
        ))}
      </div>
      
      <div className="mt-4 flex justify-between text-sm text-gray-400">
        <span>Epochs Elapsed</span>
        <span>Latest Loss: {lossData[lossData.length - 1] || '0.000'}</span>
      </div>
    </div>
  );
};
