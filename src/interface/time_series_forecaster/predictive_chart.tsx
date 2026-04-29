import React, { useState, useEffect } from 'react';

export const PredictiveChart: React.FC = () => {
  const [data, setData] = useState<number[]>([40, 42, 38, 45, 47, 43, 49, 52]);
  const [prediction, setPrediction] = useState<number | null>(null);

  useEffect(() => {
    const interval = setInterval(() => {
      setData(prev => {
        const next = [...prev.slice(1), prev[prev.length - 1] + (Math.random() * 10 - 5)];
        // LLM generates a prediction 3 steps into the future
        setPrediction(next[next.length - 1] + 8);
        return next;
      });
    }, 1500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-violet-400">Time-Series LLM</h2>
          <p className="text-xs text-slate-400">Predictive Forecasting</p>
        </div>
        <div className="w-2 h-2 rounded-full bg-violet-500 shadow-[0_0_5px_#8b5cf6]"></div>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 h-[160px] relative flex items-end gap-1">
         
         {/* Historical Data */}
         {data.map((val, i) => (
           <div key={i} className="flex-1 flex flex-col justify-end items-center h-full group">
              <div 
                className="w-full bg-slate-600 rounded-t transition-all duration-300 group-hover:bg-slate-500"
                style={{ height: `${Math.min(100, Math.max(10, val))}%` }}
              ></div>
           </div>
         ))}
         
         {/* Prediction Divider */}
         <div className="w-px h-full bg-slate-700 border-r border-dashed border-slate-500 mx-1 relative">
             <div className="absolute -top-4 left-[-15px] text-[8px] uppercase font-bold text-slate-400">Now</div>
         </div>
         
         {/* LLM Prediction */}
         {prediction && (
            <div className="flex-1 flex flex-col justify-end items-center h-full relative">
               {/* Confidence Interval */}
               <div 
                  className="absolute bottom-0 w-full bg-violet-900/30 border border-violet-800/50 rounded-t transition-all duration-300"
                  style={{ height: `${Math.min(100, Math.max(10, prediction + 15))}%` }}
               ></div>
               
               <div 
                  className="w-full bg-violet-500 rounded-t transition-all duration-300 relative z-10"
                  style={{ height: `${Math.min(100, Math.max(10, prediction))}%` }}
               ></div>
               <div className="absolute -top-5 text-[8px] text-violet-300 font-mono bg-slate-900 px-1 rounded">{prediction.toFixed(1)}</div>
            </div>
         )}
      </div>
    </div>
  );
};
