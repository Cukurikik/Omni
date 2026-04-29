import React, { useState, useEffect } from 'react';

export const OmegaPoint: React.FC = () => {
  const [timeToSingularity, setTimeToSingularity] = useState(10.0); // Seconds
  const [computeRate, setComputeRate] = useState(1e40);
  const [resurrected, setResurrected] = useState(0);
  const [transcended, setTranscended] = useState(false);

  useEffect(() => {
    // Simulate the final seconds of the universe (The Big Crunch)
    const endOfTime = setInterval(() => {
       if (!transcended) {
          setTimeToSingularity(prev => {
             // Time moves logarithmically slower subjectively as compute approaches infinity
             const next = prev * 0.9;
             
             if (next < 0.001) {
                setTranscended(true);
             }
             
             // Compute rate diverges to infinity: 1 / t
             setComputeRate(1 / next * 1e50);
             
             // Souls resurrected accelerates
             setResurrected(r => r + (1 / next * 1000000000));
             
             return next;
          });
       }
    }, 100);

    return () => clearInterval(endOfTime);
  }, [transcended]);

  return (
    <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-2xl max-w-sm mx-auto font-sans text-slate-800">
      <div className="mb-4 flex justify-between items-center border-b border-slate-200 pb-2">
        <div>
          <h2 className="text-xl font-bold text-amber-600">The Omega Point</h2>
          <p className="text-xs text-slate-500">Universal Eschatology Engine</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-bold border ${transcended ? 'bg-amber-100 text-amber-600 border-amber-300 shadow-[0_0_20px_#fcd34d]' : 'bg-slate-100 text-slate-400 border-slate-200'}`}>
          {transcended ? 'ETERNITY ACHIEVED' : 'BIG CRUNCH IMMINENT'}
        </div>
      </div>

      <div className="bg-slate-50 p-4 rounded border border-slate-200 mb-4 h-[200px] relative overflow-hidden flex items-center justify-center shadow-inner">
         
         {/* The collapsing universe */}
         <div 
            className="absolute border border-amber-200 rounded-full flex items-center justify-center transition-all duration-100 ease-linear"
            style={{
               width: `${Math.max(10, timeToSingularity * 30)}px`,
               height: `${Math.max(10, timeToSingularity * 30)}px`,
               opacity: transcended ? 0 : 1
            }}
         >
            {/* Swirling galaxies being crushed together */}
            <div className="w-full h-full rounded-full bg-[conic-gradient(from_0deg,transparent,rgba(245,158,11,0.5),transparent)] animate-[spin_0.5s_linear_infinite]"></div>
         </div>

         {/* The Omega Point Singularity */}
         <div 
            className={`absolute w-2 h-2 rounded-full transition-all duration-1000 ${transcended ? 'bg-white shadow-[0_0_100px_#f59e0b,0_0_200px_#fff] scale-[50]' : 'bg-amber-500 shadow-[0_0_20px_#f59e0b]'}`}
         ></div>

         {/* Souls being resurrected (digital rain moving towards center) */}
         {!transcended && [...Array(20)].map((_, i) => (
            <div 
               key={i}
               className="absolute w-1 h-1 bg-amber-400 rounded-full blur-[1px]"
               style={{
                  left: `${50 + (Math.random() * 100 - 50)}%`,
                  top: `${50 + (Math.random() * 100 - 50)}%`,
                  transform: `scale(${Math.random()})`,
                  animation: `move-to-center ${0.2 + Math.random() * 0.3}s ease-in infinite`
               }}
            ></div>
         ))}
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-white p-2 rounded border border-slate-200 shadow-sm">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Time to Singularity</div>
            <div className={`text-lg font-mono font-bold ${transcended ? 'text-amber-500' : 'text-slate-800'}`}>
               {transcended ? '0.000' : timeToSingularity.toFixed(3)} <span className="text-xs text-slate-400">s</span>
            </div>
         </div>
         <div className="bg-white p-2 rounded border border-slate-200 shadow-sm">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Compute Rate</div>
            <div className="text-lg font-mono font-bold text-amber-600 truncate">
               {transcended ? 'INFINITY' : `10^${Math.log10(computeRate).toFixed(0)}`} <span className="text-[10px] text-slate-400">OPS</span>
            </div>
         </div>
      </div>

      <div className="w-full bg-slate-50 rounded border border-slate-200 p-2 flex flex-col items-center">
         <span className="text-[10px] uppercase text-slate-500 mb-1">Consciousnesses Resurrected</span>
         <span className="text-xl font-mono font-bold text-slate-800">
            {transcended ? '109,000,000,000' : resurrected.toLocaleString(undefined, {maximumFractionDigits: 0})}
         </span>
      </div>

      <style>{`
        @keyframes move-to-center {
          100% { left: 50%; top: 50%; opacity: 0; }
        }
      `}</style>
    </div>
  );
};
