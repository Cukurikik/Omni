import React, { useState, useEffect } from 'react';

export const TreeViz: React.FC = () => {
  const [activeNode, setActiveNode] = useState(0);

  useEffect(() => {
    // Simulate Tree of Thoughts DFS/BFS traversal
    const interval = setInterval(() => {
      setActiveNode(prev => (prev + 1) % 5);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-teal-400">Tree of Thoughts</h2>
        <p className="text-xs text-slate-400">Monte Carlo MCTS Expansion</p>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 h-[220px] relative flex flex-col items-center">
         
         {/* Root Node */}
         <div className="w-12 h-6 bg-slate-700 rounded border border-slate-500 flex items-center justify-center text-[8px] z-10">Root</div>
         
         {/* Level 1 */}
         <div className="w-px h-6 bg-slate-600"></div>
         <div className="w-32 h-px bg-slate-600"></div>
         <div className="flex justify-between w-32 relative">
             <div className="w-px h-6 bg-slate-600 absolute left-0"></div>
             <div className="w-px h-6 bg-slate-600 absolute right-0"></div>
         </div>
         
         <div className="flex justify-between w-40 z-10">
            <div className={`w-12 h-6 rounded border flex items-center justify-center text-[8px] transition-colors ${activeNode === 0 ? 'bg-teal-600 border-teal-400 shadow-[0_0_8px_#0d9488]' : 'bg-slate-800 border-slate-600 text-slate-400'}`}>0.8 UCB</div>
            <div className={`w-12 h-6 rounded border flex items-center justify-center text-[8px] transition-colors ${activeNode === 3 ? 'bg-rose-900 border-rose-500 text-rose-300' : 'bg-slate-800 border-slate-600 text-slate-400'}`}>Pruned</div>
         </div>

         {/* Level 2 (Expanded from left node) */}
         <div className="flex w-40 mt-0">
             <div className="w-12 flex flex-col items-center">
                 <div className="w-px h-6 bg-slate-600"></div>
                 <div className="w-16 h-px bg-slate-600"></div>
                 <div className="flex justify-between w-16 relative">
                     <div className="w-px h-6 bg-slate-600 absolute left-0"></div>
                     <div className="w-px h-6 bg-slate-600 absolute right-0"></div>
                 </div>
                 <div className="flex justify-between w-20 z-10">
                     <div className={`w-8 h-6 rounded border flex items-center justify-center text-[8px] transition-colors ${activeNode === 1 ? 'bg-teal-600 border-teal-400 shadow-[0_0_8px_#0d9488]' : 'bg-slate-800 border-slate-600 text-slate-400'}`}>0.9</div>
                     <div className={`w-8 h-6 rounded border flex items-center justify-center text-[8px] transition-colors ${activeNode === 2 ? 'bg-slate-700 border-slate-500' : 'bg-slate-800 border-slate-600 text-slate-400'}`}>0.4</div>
                 </div>
             </div>
         </div>
         
      </div>
      
      <div className="mt-3 flex justify-between font-mono text-[10px] text-slate-500">
         <span>Nodes: 5</span>
         <span>Path: <span className="text-teal-400">Optimum Found</span></span>
      </div>
    </div>
  );
};
