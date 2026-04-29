import React, { useState, useEffect } from 'react';

export const DagViz: React.FC = () => {
  const [activeNode, setActiveNode] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveNode(prev => (prev + 1) % 4);
    }, 800);
    return () => clearInterval(interval);
  }, []);

  const tables = ['USERS', 'ORDERS', 'ORDER_ITEMS', 'PRODUCTS'];

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 border-b border-slate-700 pb-2">
        <h2 className="text-xl font-bold text-orange-400">Aioway DL</h2>
        <p className="text-xs text-slate-400">Relational DB Backpropagation</p>
      </div>

      <div className="flex flex-col gap-2 relative">
        {/* Draw line */}
        <div className="absolute left-[38px] top-6 bottom-6 w-0.5 bg-slate-700 -z-10"></div>

        {tables.map((t, i) => (
          <div key={t} className="flex items-center gap-4">
             <div className={`w-20 py-2 text-center rounded text-xs font-bold font-mono transition-colors duration-300
               ${activeNode === i ? 'bg-orange-500 text-slate-900 shadow-[0_0_10px_#f97316]' : 'bg-slate-800 text-slate-400 border border-slate-700'}
             `}>
               {t}
             </div>
             <div className="flex-1 text-[9px] text-slate-500 uppercase tracking-widest">
               {activeNode === i ? <span className="text-orange-400">Computing Gradients...</span> : 'Waiting...'}
             </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 bg-slate-950 px-3 py-2 rounded border border-slate-800 text-[10px] font-mono text-emerald-500">
         [LOG] Out-of-core tensor swap complete. No OOM.
      </div>
    </div>
  );
};
