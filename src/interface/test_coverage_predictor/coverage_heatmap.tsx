import React, { useState, useEffect } from 'react';

export const CoverageHeatmap: React.FC = () => {
  const [coverage, setCoverage] = useState(65);

  useEffect(() => {
    const interval = setInterval(() => {
      setCoverage(prev => {
        if (prev >= 98) {
          clearInterval(interval);
          return 98;
        }
        return prev + 3;
      });
    }, 300);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 border-b border-slate-700 pb-2">
        <h2 className="text-xl font-bold text-teal-400">Coverage Predictor</h2>
        <p className="text-xs text-slate-400">Branch Level Heatmap</p>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 text-xs font-mono relative overflow-hidden shadow-inner">
         <div className="flex gap-2 mb-1 opacity-50">
             <span className="w-4 text-right text-slate-500">1</span>
             <span className="text-teal-400">pub fn process(data: &str) {'{'}</span>
         </div>
         <div className="flex gap-2 mb-1">
             <span className="w-4 text-right text-slate-500">2</span>
             <span className="text-slate-300 ml-4">if data.is_empty() {'{'}</span>
         </div>
         <div className="flex gap-2 mb-1 relative">
             <div className={`absolute inset-0 transition-colors duration-1000 ${coverage > 70 ? 'bg-teal-900/30' : 'bg-rose-900/30'}`}></div>
             <span className="w-4 text-right text-slate-500 relative z-10">3</span>
             <span className="text-slate-400 ml-8 relative z-10">return Err("Empty");</span>
         </div>
         <div className="flex gap-2 mb-1">
             <span className="w-4 text-right text-slate-500">4</span>
             <span className="text-slate-300 ml-4">{'}'}</span>
         </div>
         <div className="flex gap-2 mb-1 relative">
             <div className={`absolute inset-0 transition-colors duration-1000 ${coverage > 90 ? 'bg-teal-900/30' : 'bg-rose-900/30'}`}></div>
             <span className="w-4 text-right text-slate-500 relative z-10">5</span>
             <span className="text-slate-400 ml-4 relative z-10">parse_complex_logic(data)</span>
         </div>
         <div className="flex gap-2">
             <span className="w-4 text-right text-slate-500">6</span>
             <span className="text-teal-400">{'}'}</span>
         </div>
      </div>
      
      <div className="mt-4 flex items-center gap-3">
         <div className="flex-1 h-2 bg-slate-800 rounded-full overflow-hidden">
            <div 
              className="h-full bg-teal-500 transition-all duration-300"
              style={{ width: `${coverage}%` }}
            ></div>
         </div>
         <span className="text-xs font-bold font-mono text-teal-400">{coverage}%</span>
      </div>
    </div>
  );
};
