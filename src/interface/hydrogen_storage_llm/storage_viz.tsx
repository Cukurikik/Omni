import React, { useState, useEffect } from 'react';

export const StorageViz: React.FC = () => {
  const [pressure, setPressure] = useState(10); // starting bar

  useEffect(() => {
    // Simulate LLM analyzing a Metal-Organic Framework (MOF)
    const interval = setInterval(() => {
      setPressure(prev => {
        if (prev >= 700) return 700;
        return prev + 50;
      });
    }, 200);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-yellow-500">H2 Storage LLM</h2>
        <p className="text-xs text-slate-400">Material Property Analyzer</p>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800">
        <div className="flex justify-between items-center mb-2">
            <span className="text-xs uppercase font-bold text-slate-500">Thermodynamic State</span>
            <span className="text-xs font-mono text-yellow-400">{pressure} Bar</span>
        </div>
        
        {/* Pressure Gauge Vis */}
        <div className="w-full h-4 bg-slate-800 rounded-full overflow-hidden relative">
            <div 
              className={`h-full transition-all duration-200 ${pressure > 350 ? 'bg-rose-500' : 'bg-yellow-500'}`}
              style={{ width: `${(pressure / 700) * 100}%` }}
            />
            {/* 350 Bar marker */}
            <div className="absolute top-0 bottom-0 left-1/2 w-px bg-white/50"></div>
        </div>
        
        <div className="mt-4 text-xs font-mono text-white border-t border-slate-800 pt-3">
          <span className="text-emerald-400">LLM Output:</span> Based on the Van der Waals properties, this MOF candidate requires {pressure > 350 ? 'Type IV' : 'Type I'} composite tanks.
        </div>
      </div>
    </div>
  );
};
