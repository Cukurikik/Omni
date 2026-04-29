import React, { useState, useEffect } from 'react';

export const CostFactorViz: React.FC = () => {
  const [factors, setFactors] = useState<{cost: number, timeMs: number}[]>([]);

  useEffect(() => {
    // Generate deterministic exponential curve for bcrypt cost
    const data = [];
    let baseTime = 20; // 20ms for cost 10
    
    for (let c = 10; c <= 14; c++) {
      data.push({ cost: c, timeMs: baseTime });
      baseTime *= 2; // Roughly doubles every cost factor
    }
    setFactors(data);
  }, []);

  return (
    <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-xl max-w-sm mx-auto font-sans">
      <div className="mb-6 border-b border-slate-200 pb-2">
        <h2 className="text-xl font-bold text-slate-800">Bcrypt KDF</h2>
        <p className="text-xs text-slate-500">Exponential Work Factor Scaling</p>
      </div>

      <div className="flex flex-col gap-4">
        {factors.map(f => (
          <div key={f.cost} className="relative">
            <div className="flex justify-between text-xs font-bold text-slate-600 mb-1">
              <span>Cost: {f.cost}</span>
              <span className="font-mono">{f.timeMs} ms</span>
            </div>
            <div className="h-4 bg-slate-100 rounded overflow-hidden relative border border-slate-200">
              <div 
                className="h-full bg-slate-800" 
                style={{ width: `${(f.timeMs / factors[factors.length-1].timeMs) * 100}%` }}
              ></div>
            </div>
            
            {f.cost === 12 && (
              <div className="absolute top-0 right-16 text-[8px] bg-emerald-100 text-emerald-700 px-1 py-0.5 rounded border border-emerald-300 font-bold">
                RECOMMENDED
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
