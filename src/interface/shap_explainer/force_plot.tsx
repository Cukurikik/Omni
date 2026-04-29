import React, { useState, useEffect } from 'react';

export const ForcePlot: React.FC = () => {
  const [features, setFeatures] = useState<{name: string, value: number, shap: number}[]>([]);
  const baseValue = 0.5;

  useEffect(() => {
    // Deterministic SHAP value generation
    const initial = [
      { name: 'Age', value: 45, shap: 0.15 },
      { name: 'Income', value: 85000, shap: 0.22 },
      { name: 'Debt', value: 15000, shap: -0.18 },
      { name: 'CreditScore', value: 680, shap: -0.05 },
      { name: 'Employed', value: 1, shap: 0.08 }
    ];
    
    setFeatures(initial);
  }, []);

  const totalShap = features.reduce((acc, f) => acc + f.shap, 0);
  const finalValue = baseValue + totalShap;

  // Separate positive (pushing output higher) and negative (pushing output lower)
  const posFeatures = [...features].filter(f => f.shap > 0).sort((a,b) => b.shap - a.shap);
  const negFeatures = [...features].filter(f => f.shap < 0).sort((a,b) => a.shap - b.shap);

  return (
    <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-xl max-w-3xl mx-auto font-sans">
      <div className="mb-8 border-b border-slate-200 pb-2">
        <h2 className="text-xl font-bold text-slate-800">SHAP Force Plot</h2>
        <p className="text-xs text-slate-500">Local Model Interpretability</p>
      </div>

      <div className="relative mt-10 mb-20 h-16 w-full flex items-center justify-center">
        
        {/* Base Value Line */}
        <div className="absolute top-0 bottom-0 border-l border-dashed border-slate-400" style={{ left: '30%' }}>
          <div className="absolute -top-6 -translate-x-1/2 text-[10px] text-slate-500">base value<br/><b>{baseValue.toFixed(2)}</b></div>
        </div>

        {/* Output Value Line */}
        <div className="absolute top-0 bottom-0 border-l-2 border-slate-800 z-10" style={{ left: '52%' }}>
          <div className="absolute top-full mt-2 -translate-x-1/2 text-xs font-bold text-slate-800">
            {finalValue.toFixed(2)}<br/>
            <span className="text-[10px] font-normal text-slate-500">f(x)</span>
          </div>
        </div>

        {/* Force Bars */}
        <div className="flex w-full h-8 absolute items-center">
          
          {/* Positive forces (Pushing right, colored red/pink in SHAP) */}
          <div className="flex justify-end relative h-full group" style={{ width: '52%', right: '48%' }}>
            {posFeatures.map((f, i) => (
              <div 
                key={i} 
                className="h-full bg-rose-500 border-r border-white relative flex items-center justify-center overflow-hidden"
                style={{ width: `${(f.shap / totalShap) * 50}%` }}
              >
                {f.shap > 0.05 && <span className="text-[8px] text-white font-bold truncate px-1">{f.name}</span>}
              </div>
            ))}
            <div className="absolute -bottom-6 right-0 text-[10px] font-bold text-rose-500">higher ←</div>
          </div>

          {/* Negative forces (Pushing left, colored blue in SHAP) */}
          <div className="flex justify-start relative h-full group" style={{ width: '48%', left: '52%' }}>
            {negFeatures.map((f, i) => (
              <div 
                key={i} 
                className="h-full bg-blue-500 border-l border-white relative flex items-center justify-center overflow-hidden"
                style={{ width: `${(Math.abs(f.shap) / Math.abs(totalShap)) * 40}%` }}
              >
                 {Math.abs(f.shap) > 0.05 && <span className="text-[8px] text-white font-bold truncate px-1">{f.name}</span>}
              </div>
            ))}
             <div className="absolute -bottom-6 left-0 text-[10px] font-bold text-blue-500">→ lower</div>
          </div>

        </div>
      </div>
    </div>
  );
};
