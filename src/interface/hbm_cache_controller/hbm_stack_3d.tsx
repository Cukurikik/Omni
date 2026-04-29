import React, { useState, useEffect } from 'react';

export const HbmStack3D: React.FC = () => {
  const [activeDie, setActiveDie] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate rapid memory access across the 3D stacked DRAM dies
      setActiveDie(Math.floor(Math.random() * 8)); // 8-Hi HBM stack
    }, 100);
    return () => clearInterval(interval);
  }, []);

  // 8 DRAM Dies in an HBM stack
  const dies = Array.from({ length: 8 });

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-indigo-400">HBM3 Memory</h2>
          <p className="text-xs text-slate-400">3D Stacked Architecture</p>
        </div>
        <div className="px-2 py-1 bg-indigo-900/30 text-indigo-400 text-[10px] font-mono rounded border border-indigo-800">
          3.2 TB/s
        </div>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 h-[220px] relative flex flex-col items-center justify-end pb-8 mb-4 perspective-1000">
         
         {/* HBM 3D Stack */}
         <div className="relative w-32 flex flex-col items-center transform -rotate-x-12">
            {dies.map((_, i) => {
               // Render dies from top (7) to bottom (0)
               const reverseIdx = 7 - i;
               const isActive = activeDie === reverseIdx;
               return (
                  <div 
                     key={reverseIdx}
                     className={`w-full h-4 border-t border-x transition-all duration-75 relative
                        ${isActive ? 'bg-indigo-500 border-indigo-300 z-20' : 'bg-slate-800 border-slate-600 z-10'}
                     `}
                     style={{
                        marginBottom: '-2px', // Stack overlap
                        transform: isActive ? 'scale(1.05)' : 'scale(1)',
                        boxShadow: isActive ? '0 -5px 15px rgba(99, 102, 241, 0.5)' : 'none'
                     }}
                  >
                     {/* TSV (Through Silicon Via) Simulators */}
                     <div className="absolute inset-0 flex justify-evenly items-center opacity-30">
                        <div className="w-1 h-full bg-slate-900"></div>
                        <div className="w-1 h-full bg-slate-900"></div>
                        <div className="w-1 h-full bg-slate-900"></div>
                     </div>
                  </div>
               );
            })}
            
            {/* Logic Base Die */}
            <div className="w-full h-6 bg-slate-700 border border-slate-500 rounded-b mt-[2px] flex items-center justify-center shadow-lg z-30">
               <span className="text-[8px] font-bold text-slate-300 tracking-widest">LOGIC BASE</span>
            </div>
            
            {/* Silicon Interposer Simulator */}
            <div className="w-[120%] h-2 bg-emerald-900/50 border-t border-emerald-800 mt-2 z-0 relative">
               <div className="absolute inset-x-0 bottom-0 h-[1px] bg-emerald-500/50 shadow-[0_0_5px_#10b981] animate-pulse"></div>
            </div>
         </div>
      </div>
      
      <div className="flex justify-between text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Die Hit: {activeDie}</span>
         <span>TSV Link: Active</span>
         <span>ECC Status: <span className="text-emerald-400">Clean</span></span>
      </div>
    </div>
  );
};
