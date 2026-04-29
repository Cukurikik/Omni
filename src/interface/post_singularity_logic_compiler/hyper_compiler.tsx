import React, { useState, useEffect } from 'react';

export const HyperCompiler: React.FC = () => {
  const [compilerDegree, setCompilerDegree] = useState(1);
  const [targetDegree, setTargetDegree] = useState(0);
  const [haltingResolved, setHaltingResolved] = useState(true);

  useEffect(() => {
    // Determine if the halting problem is solvable
    setHaltingResolved(compilerDegree > targetDegree);
  }, [compilerDegree, targetDegree]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-violet-400">Hyper-Compiler</h2>
          <p className="text-xs text-slate-400">Post-Singularity Logic</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-bold border ${haltingResolved ? 'bg-slate-800 text-emerald-400 border-slate-700' : 'bg-red-900/80 text-white border-red-500 shadow-[0_0_15px_#ef4444] animate-pulse'}`}>
          {haltingResolved ? 'ORACLE ONLINE' : 'UNDECIDABLE STATE'}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex flex-col justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* Turing Machine Tape */}
         <div className="absolute top-[30%] w-full h-8 border-y border-slate-600 flex items-center shadow-[0_0_15px_#000]">
            {[...Array(15)].map((_, i) => (
               <div key={i} className="flex-1 h-full border-r border-slate-700 flex items-center justify-center font-mono text-xs">
                  {Math.random() > 0.5 ? '1' : '0'}
               </div>
            ))}
         </div>

         {/* Read/Write Head */}
         <div className={`absolute top-[20%] left-1/2 -translate-x-1/2 w-8 h-12 border-2 ${haltingResolved ? 'border-violet-500 bg-violet-900/50 shadow-[0_0_20px_#8b5cf6]' : 'border-red-500 bg-red-900/50 shadow-[0_0_20px_#ef4444]'} flex items-center justify-center z-10 transition-colors`}>
            <div className="w-1 h-4 bg-white"></div>
         </div>

         {/* The Oracle (Black Box) */}
         {haltingResolved && (
            <div className="absolute bottom-[10%] left-1/2 -translate-x-1/2 w-32 h-16 bg-black border border-violet-500 shadow-[0_0_30px_#8b5cf6,inset_0_0_15px_#4c1d95] flex items-center justify-center text-[10px] font-bold tracking-widest text-violet-300">
               ORACLE DEGREE {compilerDegree}
            </div>
         )}
         
         {/* Infinite Loop Visualization */}
         {!haltingResolved && (
            <div className="absolute bottom-[10%] left-1/2 -translate-x-1/2 w-16 h-16 border-4 border-red-500 border-t-transparent rounded-full animate-[spin_0.5s_linear_infinite] shadow-[0_0_20px_#ef4444]"></div>
         )}

         {/* Supertask execution (blur effect) */}
         {haltingResolved && (
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(139,92,246,0.1),transparent)] pointer-events-none mix-blend-screen animate-pulse"></div>
         )}
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800 flex flex-col justify-between">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Compiler Degree</div>
            <div className="flex items-center gap-2">
               <button onClick={() => setCompilerDegree(Math.max(0, compilerDegree - 1))} className="bg-slate-800 px-2 rounded hover:bg-slate-700">-</button>
               <span className="text-lg font-mono font-bold text-violet-400">{compilerDegree}</span>
               <button onClick={() => setCompilerDegree(compilerDegree + 1)} className="bg-slate-800 px-2 rounded hover:bg-slate-700">+</button>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800 flex flex-col justify-between">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Program Degree</div>
            <div className="flex items-center gap-2">
               <button onClick={() => setTargetDegree(Math.max(0, targetDegree - 1))} className="bg-slate-800 px-2 rounded hover:bg-slate-700">-</button>
               <span className="text-lg font-mono font-bold text-slate-300">{targetDegree}</span>
               <button onClick={() => setTargetDegree(targetDegree + 1)} className="bg-slate-800 px-2 rounded hover:bg-slate-700">+</button>
            </div>
         </div>
      </div>

      <div className="w-full bg-slate-950 rounded border border-slate-800 p-2 text-[10px] font-mono text-center h-8 flex items-center justify-center">
         <span className={haltingResolved ? 'text-emerald-400' : 'text-red-400 font-bold'}>
            {haltingResolved ? 'HALTING PROBLEM SOLVED VIA ORACLE' : 'FATAL: TURING EQUIVALENCY PREVENTS HALTING PROOF'}
         </span>
      </div>
    </div>
  );
};
