import React, { useState, useEffect } from 'react';

export const VramVisualizer: React.FC = () => {
  const [blocks, setBlocks] = useState<{id: number, size: number, used: boolean, type: string}[]>([]);

  useEffect(() => {
    // Generate simulated VRAM chunks (Total 24GB RTX 4090)
    const initial = Array.from({ length: 48 }).map((_, i) => ({
      id: i,
      size: 512, // 512MB blocks
      used: Math.random() > 0.4,
      type: Math.random() > 0.5 ? 'weights' : 'kv_cache'
    }));
    setBlocks(initial);

    const interval = setInterval(() => {
      setBlocks(prev => {
        const next = [...prev];
        // Simulate fragmentation and memory churn
        const idx = Math.floor(Math.random() * next.length);
        next[idx] = { ...next[idx], used: !next[idx].used };
        return next;
      });
    }, 400);

    return () => clearInterval(interval);
  }, []);

  const usedBlocks = blocks.filter(b => b.used).length;
  const totalBlocks = blocks.length;
  const usagePct = ((usedBlocks / totalBlocks) * 100).toFixed(1);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-green-500">GPU VRAM</h2>
          <p className="text-xs text-slate-400">Tensor Allocator (RTX 4090)</p>
        </div>
        <div className="text-[10px] font-mono bg-green-900/50 text-green-400 border border-green-800 px-2 py-1 rounded">
           {usagePct}% USED
        </div>
      </div>

      <div className="bg-slate-950 p-2 rounded border border-slate-800 h-[180px] flex flex-wrap gap-1 content-start mb-4">
         {blocks.map((b) => (
           <div 
             key={b.id}
             className={`w-[calc(12.5%-4px)] h-4 rounded-sm transition-colors duration-300 ${
               !b.used ? 'bg-slate-800' : 
               b.type === 'weights' ? 'bg-indigo-500 shadow-[0_0_8px_#6366f1]' : 
               'bg-teal-500 shadow-[0_0_8px_#14b8a6]'
             }`}
             title={!b.used ? 'Free 512MB' : `${b.type} 512MB`}
           ></div>
         ))}
      </div>
      
      <div className="flex justify-between text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <div className="flex items-center gap-1"><div className="w-2 h-2 bg-indigo-500 rounded-sm"></div> Model Weights</div>
         <div className="flex items-center gap-1"><div className="w-2 h-2 bg-teal-500 rounded-sm"></div> KV Cache</div>
         <div className="flex items-center gap-1"><div className="w-2 h-2 bg-slate-700 rounded-sm"></div> Free</div>
      </div>
    </div>
  );
};
