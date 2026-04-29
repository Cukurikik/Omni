import React, { useState, useEffect } from 'react';

export const CapsuleViz: React.FC = () => {
  const [coupling, setCoupling] = useState<number[][]>(Array(4).fill(Array(3).fill(0.33)));

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate dynamic routing convergence
      setCoupling(prev => prev.map(row => {
        const targetIdx = Math.floor(Math.random() * 3);
        return row.map((val, i) => {
          if (i === targetIdx) return Math.min(1.0, val + 0.1);
          return Math.max(0.0, val - 0.05);
        });
      }));
    }, 800);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 border-b border-slate-700 pb-2">
        <h2 className="text-xl font-bold text-rose-400">Capsule Network</h2>
        <p className="text-xs text-slate-400">Dynamic Routing by Agreement</p>
      </div>

      <div className="flex justify-between items-center mb-4 text-xs font-mono text-slate-500 px-4">
         <div>PrimaryCaps</div>
         <div>DigitCaps</div>
      </div>

      <div className="relative h-40 flex justify-between px-6">
         {/* Layer 1 */}
         <div className="flex flex-col justify-between h-full z-10">
           {[0,1,2,3].map(i => (
             <div key={`in-${i}`} className="w-4 h-4 rounded-full bg-slate-600 shadow-[0_0_5px_#475569]"></div>
           ))}
         </div>

         {/* Routing Weights (Lines) */}
         <div className="absolute inset-0 pointer-events-none opacity-60">
            <svg width="100%" height="100%">
              {[0,1,2,3].map(i => 
                [0,1,2].map(j => {
                  const y1 = 12 + i * (100 / 3) + "%";
                  const y2 = 20 + j * 50 + "%";
                  const weight = coupling[i][j];
                  return (
                    <line key={`l-${i}-${j}`} x1="15%" y1={y1} x2="85%" y2={y2} 
                          stroke="#fb7185" strokeWidth={weight * 3} strokeOpacity={weight} />
                  )
                })
              )}
            </svg>
         </div>

         {/* Layer 2 */}
         <div className="flex flex-col justify-around h-full z-10">
           {[0,1,2].map(i => (
             <div key={`out-${i}`} className="w-6 h-6 rounded bg-rose-500 shadow-[0_0_10px_#f43f5e] flex items-center justify-center text-[8px] font-bold">
               {i}
             </div>
           ))}
         </div>
      </div>
    </div>
  );
};
