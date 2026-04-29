import React, { useState, useEffect } from 'react';

export const GroundedVQA: React.FC = () => {
  const [analyzing, setAnalyzing] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setAnalyzing(false);
    }, 2500);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 border-b border-slate-700 pb-2">
        <h2 className="text-xl font-bold text-lime-400">Grounded VQA</h2>
        <p className="text-xs text-slate-400">Visual Question Answering</p>
      </div>

      <div className="bg-slate-800 p-2 rounded mb-4 text-xs font-mono border border-slate-600">
         <span className="text-lime-400 font-bold">Query:</span> "Identify the anomalous components on the circuit board."
      </div>

      <div className="bg-slate-950 rounded border border-slate-800 h-[180px] relative overflow-hidden flex items-center justify-center mb-4">
         {/* Simulated Image */}
         <div className="absolute inset-0 bg-slate-800 opacity-50" style={{
            backgroundImage: 'repeating-linear-gradient(45deg, #1e293b 25%, transparent 25%, transparent 75%, #1e293b 75%, #1e293b), repeating-linear-gradient(45deg, #1e293b 25%, #0f172a 25%, #0f172a 75%, #1e293b 75%, #1e293b)',
            backgroundPosition: '0 0, 10px 10px',
            backgroundSize: '20px 20px'
         }}></div>
         
         {analyzing ? (
            <div className="relative z-10 flex flex-col items-center">
               <div className="w-8 h-8 border-4 border-lime-500 border-t-transparent rounded-full animate-spin"></div>
               <div className="text-[10px] uppercase font-bold text-lime-500 mt-2 tracking-widest animate-pulse">Encoding Image...</div>
            </div>
         ) : (
            <>
               {/* Grounding Bounding Box 1 */}
               <div className="absolute top-[20%] left-[30%] w-[15%] h-[25%] border-2 border-rose-500 bg-rose-500/20 animate-fade-in group">
                   <div className="absolute -top-4 left-[-2px] bg-rose-500 text-white text-[8px] px-1 font-bold">Burnt Resistor (0.94)</div>
               </div>
               
               {/* Grounding Bounding Box 2 */}
               <div className="absolute top-[60%] left-[65%] w-[20%] h-[15%] border-2 border-amber-500 bg-amber-500/20 animate-fade-in" style={{animationDelay: '300ms'}}>
                   <div className="absolute -top-4 left-[-2px] bg-amber-500 text-white text-[8px] px-1 font-bold">Missing Cap (0.88)</div>
               </div>
            </>
         )}
      </div>

      {!analyzing && (
         <div className="bg-slate-950 p-3 rounded border border-lime-900/50 text-xs text-lime-300 font-mono shadow-[0_0_10px_rgba(132,204,22,0.1)]">
            "I detected two anomalies. There is a burnt resistor in the top-left quadrant and a missing capacitor in the lower-right area."
         </div>
      )}
    </div>
  );
};
