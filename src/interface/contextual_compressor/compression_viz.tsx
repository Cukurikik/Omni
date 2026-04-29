import React, { useState, useEffect } from 'react';

export const CompressionViz: React.FC = () => {
  const [tokens, setTokens] = useState(12400);
  const [compressed, setCompressed] = useState(12400);

  useEffect(() => {
    // Simulate Contextual Compression taking effect
    const interval = setInterval(() => {
      setCompressed(prev => {
        if (prev <= 3100) return 3100;
        return prev - 850;
      });
    }, 150);

    return () => clearInterval(interval);
  }, []);

  const ratio = ((1 - (compressed / tokens)) * 100).toFixed(0);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 border-b border-slate-700 pb-2">
        <h2 className="text-xl font-bold text-orange-400">Contextual Compressor</h2>
        <p className="text-xs text-slate-400">Semantic Token Filtering</p>
      </div>

      <div className="flex justify-between items-center mb-6">
         <div className="text-center">
             <div className="text-2xl font-mono text-slate-300">{tokens}</div>
             <div className="text-[10px] text-slate-500 uppercase mt-1">Raw Tokens</div>
         </div>
         
         <div className="flex flex-col items-center">
             <div className="text-xs text-orange-400 font-bold mb-1">-{ratio}%</div>
             <div className="text-2xl">⚡</div>
         </div>
         
         <div className="text-center">
             <div className="text-2xl font-mono text-emerald-400">{compressed}</div>
             <div className="text-[10px] text-slate-500 uppercase mt-1">LLM Input</div>
         </div>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 text-xs text-slate-400 leading-relaxed font-mono relative overflow-hidden">
         {/* Simulated compression visualization */}
         <span>The </span>
         <span className={compressed < 8000 ? "opacity-20 line-through text-slate-600 transition-all duration-500" : ""}>highly detailed and exhaustive </span>
         <span>financial report </span>
         <span className={compressed < 5000 ? "opacity-20 line-through text-slate-600 transition-all duration-500" : ""}>which was published last week </span>
         <span>shows Q3 revenue grew </span>
         <span className={compressed < 3500 ? "opacity-20 line-through text-slate-600 transition-all duration-500" : ""}>by a staggering margin of </span>
         <span>14%.</span>
         
         <div className="mt-3 pt-3 border-t border-slate-800 flex justify-between text-[10px]">
             <span>Cost Saved: ${(tokens - compressed) * 0.00002.toFixed(4)}</span>
             <span>Latency Reduced: 45ms</span>
         </div>
      </div>
    </div>
  );
};
