import React, { useState, useEffect } from 'react';

export const SnarkProgress: React.FC = () => {
  const [progress, setProgress] = useState(0);
  const [phase, setPhase] = useState('Witness Generation');

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress(prev => {
         const next = prev + 2;
         if (next >= 100) {
            clearInterval(interval);
            setPhase('Proof Complete');
            return 100;
         }
         
         if (next > 70) setPhase('Polynomial Commitment (KZG)');
         else if (next > 40) setPhase('Multi-Scalar Multiplication (MSM)');
         else if (next > 20) setPhase('Number Theoretic Transform (NTT)');
         
         return next;
      });
    }, 150);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-violet-400">zk-SNARK Prover</h2>
          <p className="text-xs text-slate-400">Groth16 Zero-Knowledge Proof</p>
        </div>
        <div className="text-[10px] font-mono bg-violet-900/30 text-violet-400 border border-violet-800 px-2 py-1 rounded">
          GPU Cluster
        </div>
      </div>

      <div className="bg-slate-950 p-6 rounded border border-slate-800 flex flex-col items-center justify-center mb-4">
         {/* Circular Progress */}
         <div className="relative w-24 h-24 mb-4">
            <svg className="w-full h-full" viewBox="0 0 100 100">
               <circle cx="50" cy="50" r="45" fill="none" stroke="#1e293b" strokeWidth="8" />
               <circle 
                  cx="50" cy="50" r="45" fill="none" stroke="#8b5cf6" strokeWidth="8" 
                  strokeDasharray="283" strokeDashoffset={283 - (283 * progress) / 100}
                  strokeLinecap="round" transform="rotate(-90 50 50)"
                  className="transition-all duration-300 ease-out"
               />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center flex-col">
               <span className="text-xl font-mono font-bold text-white">{progress}%</span>
            </div>
         </div>
         
         <div className="text-xs font-mono text-violet-300 animate-pulse text-center">
            {phase}...
         </div>
      </div>
      
      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Curve: <span className="text-white">BN254</span></span>
         <span>Constraints: <span className="text-emerald-400">2^24</span></span>
         <span className="col-span-2 text-slate-500">Target: Proof of Reserves Verification</span>
      </div>
    </div>
  );
};
