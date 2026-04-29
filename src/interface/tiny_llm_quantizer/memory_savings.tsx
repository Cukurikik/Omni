import React, { useState, useEffect } from 'react';

export const MemorySavings: React.FC = () => {
  const [quantizing, setQuantizing] = useState(true);
  const [size, setSize] = useState(7.2); // GB for FP16 Llama 7B

  useEffect(() => {
    const interval = setInterval(() => {
      setSize(prev => {
        if (prev <= 3.8) {
          setQuantizing(false);
          clearInterval(interval);
          return 3.8; // GB for INT4
        }
        return prev - 0.4;
      });
    }, 150);
    return () => clearInterval(interval);
  }, []);

  const progress = ((7.2 - size) / (7.2 - 3.8)) * 100;

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 border-b border-slate-700 pb-2">
        <h2 className="text-xl font-bold text-fuchsia-400">TinyLLM Quantizer</h2>
        <p className="text-xs text-slate-400">Edge Device Memory Compression</p>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 text-center mb-4 relative overflow-hidden">
         <div className="text-[10px] uppercase font-bold text-slate-500 mb-1">Model Footprint (Llama-7B)</div>
         <div className={`text-4xl font-mono transition-colors ${quantizing ? 'text-rose-500' : 'text-emerald-500 font-bold'}`}>
            {size.toFixed(1)} GB
         </div>
         <div className="text-[10px] text-slate-400 mt-1">{quantizing ? 'FP16 -> INT4 Quantization...' : 'INT4 Quantization Complete'}</div>
      </div>

      <div className="space-y-3">
         <div className="w-full h-4 bg-slate-800 rounded-full overflow-hidden relative">
            <div 
              className="absolute top-0 left-0 h-full bg-rose-500 transition-all duration-300"
              style={{ width: `${(size / 8) * 100}%` }}
            ></div>
            {/* Target Marker */}
            <div className="absolute top-0 bottom-0 w-px bg-white z-10" style={{ left: `${(3.8 / 8) * 100}%` }}></div>
         </div>
         
         <div className="grid grid-cols-2 gap-2 text-[10px] font-mono">
            <div className="bg-slate-800 p-2 rounded border border-slate-700">
               <span className="text-slate-500 block">VRAM Required</span>
               <span className={quantizing ? 'text-rose-400' : 'text-emerald-400'}>{quantizing ? '> 8 GB' : '< 4 GB'}</span>
            </div>
            <div className="bg-slate-800 p-2 rounded border border-slate-700">
               <span className="text-slate-500 block">Perplexity (PPL)</span>
               <span className="text-amber-400">5.82 → 5.91</span>
            </div>
         </div>
      </div>
    </div>
  );
};
