import React, { useState, useEffect } from 'react';

export const ForecastViz: React.FC = () => {
  const [history, setHistory] = useState<number[]>(Array(20).fill(0).map(() => Math.random() * 50 + 20));
  const [forecast, setForecast] = useState<number[]>([]);
  const [bounds, setBounds] = useState<{upper: number[], lower: number[]}>({upper: [], lower: []});

  useEffect(() => {
    // Generate prediction
    const lastVal = history[history.length - 1];
    const newForecast = [];
    const newUpper = [];
    const newLower = [];
    
    let current = lastVal;
    for (let i = 0; i < 10; i++) {
      current += (Math.random() - 0.5) * 10;
      newForecast.push(current);
      // Uncertainty increases over time
      const uncertainty = i * 3;
      newUpper.push(current + uncertainty);
      newLower.push(current - uncertainty);
    }
    
    setForecast(newForecast);
    setBounds({upper: newUpper, lower: newLower});
  }, [history]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 border-b border-slate-700 pb-2 flex justify-between">
        <div>
          <h2 className="text-xl font-bold text-teal-400">TFT Forecaster</h2>
          <p className="text-xs text-slate-400">Temporal Fusion Transformer</p>
        </div>
        <div className="text-[10px] text-teal-500 font-bold">p10 / p50 / p90</div>
      </div>

      <div className="relative h-32 bg-slate-950 p-2 rounded border border-slate-800 flex items-end gap-1">
        {/* History Area */}
        <div className="flex items-end gap-[2px] w-2/3 h-full border-r border-slate-700 border-dashed pr-2">
          {history.map((h, i) => (
             <div key={`h-${i}`} className="flex-1 bg-slate-600 transition-all duration-300" style={{height: `${h}%`}}></div>
          ))}
        </div>
        
        {/* Forecast Area */}
        <div className="flex items-end gap-[2px] w-1/3 h-full pl-2 relative">
          {forecast.map((f, i) => (
            <div key={`f-${i}`} className="relative flex-1 h-full flex items-end justify-center">
              {/* Uncertainty bound */}
              <div className="absolute w-full bg-teal-900/30 transition-all" style={{
                bottom: `${bounds.lower[i]}%`, 
                height: `${bounds.upper[i] - bounds.lower[i]}%`
              }}></div>
              {/* Median prediction */}
              <div className="absolute w-full bg-teal-400 z-10" style={{height: `${f}%`}}></div>
            </div>
          ))}
        </div>
      </div>
      
      <div className="mt-2 flex justify-between text-[10px] text-slate-500 font-bold uppercase">
         <span>History: t-20</span>
         <span>Horizon: t+10</span>
      </div>
    </div>
  );
};
