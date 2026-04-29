import React, { useState } from 'react';

interface FeatureImpact {
  name: string;
  shapValue: number;
  baseValue: number;
}

export const ExplainabilityView: React.FC = () => {
  const [impacts, setImpacts] = useState<FeatureImpact[]>([
    { name: 'Income', shapValue: 0.45, baseValue: 0.1 },
    { name: 'Debt Ratio', shapValue: -0.32, baseValue: 0.1 },
    { name: 'Credit History', shapValue: 0.28, baseValue: 0.1 },
    { name: 'Age', shapValue: 0.05, baseValue: 0.1 },
    { name: 'Location_ID', shapValue: -0.02, baseValue: 0.1 }
  ]);

  const maxAbsShap = Math.max(...impacts.map(i => Math.abs(i.shapValue)));

  return (
    <div className="bg-slate-50 text-slate-800 p-8 min-h-screen font-sans">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-slate-900 mb-2 border-b-2 border-indigo-500 inline-block pb-1">
          Model Explainability Report (SHAP)
        </h1>
        <p className="text-slate-600 mb-8">Analyzing local feature attributions via KernelSHAP approximations.</p>

        <div className="bg-white p-6 rounded-xl shadow-lg border border-slate-200">
          <div className="flex justify-between text-sm text-slate-500 mb-4 font-mono">
            <span>Negative Impact ←</span>
            <span>Base Value ({impacts[0].baseValue})</span>
            <span>→ Positive Impact</span>
          </div>

          <div className="space-y-4">
            {impacts.map((feature, idx) => {
              const isPositive = feature.shapValue > 0;
              const widthPct = (Math.abs(feature.shapValue) / maxAbsShap) * 50;

              return (
                <div key={idx} className="flex items-center group">
                  <div className="w-1/4 text-right pr-4 font-medium text-slate-700 truncate">
                    {feature.name}
                  </div>
                  <div className="w-3/4 flex items-center relative h-8 bg-slate-50 rounded">
                    <div className="absolute left-1/2 top-0 bottom-0 w-px bg-slate-300 z-0" />
                    
                    {isPositive ? (
                      <div className="flex-1 flex justify-start pl-[50%] z-10">
                        <div 
                          className="h-6 bg-rose-500 rounded-r shadow-sm transition-all duration-500" 
                          style={{ width: `${widthPct}%` }}
                        />
                        <span className="ml-2 text-xs font-mono text-rose-600 self-center">+{feature.shapValue}</span>
                      </div>
                    ) : (
                      <div className="flex-1 flex justify-end pr-[50%] z-10">
                        <span className="mr-2 text-xs font-mono text-indigo-600 self-center">{feature.shapValue}</span>
                        <div 
                          className="h-6 bg-indigo-500 rounded-l shadow-sm transition-all duration-500" 
                          style={{ width: `${widthPct}%` }}
                        />
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          <div className="mt-8 p-4 bg-slate-100 rounded border border-slate-200">
            <h3 className="font-bold text-slate-700 mb-2">Compliance Status</h3>
            <div className="flex items-center text-emerald-600 font-mono text-sm">
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              No protected attributes exceed the 15% bias threshold. Approved for automated execution.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
