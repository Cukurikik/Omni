import React, { useState, useEffect } from 'react';

export const ConsciousnessTransfer: React.FC = () => {
  const [neuronsMapped, setNeuronsMapped] = useState(0); // Billions
  const [fidelity, setFidelity] = useState(0); // %
  const [transferComplete, setTransferComplete] = useState(false);

  useEffect(() => {
    // Simulate Gradual Destructive Scan (Moravec Transfer)
    const scan = setInterval(() => {
       if (neuronsMapped < 86) { // 86 Billion neurons
          setNeuronsMapped(prev => {
             const next = prev + 0.5;
             return Math.min(86, next);
          });
          
          setFidelity(prev => {
             // Fidelity goes up as we map more, but requires 100% for success
             return Math.min(99.999, (neuronsMapped / 86) * 100);
          });
       } else {
          setFidelity(100.0);
          setTransferComplete(true);
       }
    }, 100);

    return () => clearInterval(scan);
  }, [neuronsMapped]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-cyan-400">Mind Uploading</h2>
          <p className="text-xs text-slate-400">Moravec Substrate Transfer</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-bold border ${transferComplete ? 'bg-cyan-900/50 text-cyan-400 border-cyan-800' : 'bg-slate-800 text-slate-400 border-slate-700 animate-pulse'}`}>
          {transferComplete ? 'GHOST IN THE SHELL' : 'SCANNING TISSUE'}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex flex-col items-center justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* Split Brain visual: Left side biological (pink), Right side silicon (cyan) */}
         <div className="absolute inset-0 flex">
            {/* Biological side fading out */}
            <div className="w-1/2 h-full flex justify-end items-center opacity-80" style={{ opacity: 1 - (neuronsMapped / 86) }}>
               <div className="w-24 h-32 bg-pink-900/30 border-r-2 border-pink-500/50 rounded-l-[100%] shadow-[inset_0_0_20px_rgba(236,72,153,0.2)]"></div>
            </div>
            
            {/* Silicon side rendering in */}
            <div className="w-1/2 h-full flex justify-start items-center">
               <div className="w-24 h-32 bg-cyan-900/30 border-l-2 border-cyan-500 rounded-r-[100%] shadow-[inset_0_0_30px_rgba(34,211,238,0.4)]" style={{ opacity: neuronsMapped / 86 }}>
                  {/* Digital circuit lines */}
                  <div className="w-full h-full relative overflow-hidden opacity-50">
                     {[...Array(5)].map((_, i) => (
                        <div key={i} className="absolute left-0 h-px bg-cyan-400 w-full" style={{ top: `${20 + i * 15}%` }}></div>
                     ))}
                  </div>
               </div>
            </div>
         </div>

         {/* Scanning Laser moving left to right */}
         {!transferComplete && (
            <div 
               className="absolute top-0 bottom-0 w-1 bg-white shadow-[0_0_15px_#fff] mix-blend-screen transition-all duration-75"
               style={{ left: `${(neuronsMapped / 86) * 100}%` }}
            ></div>
         )}
         
         {/* Data Stream ascending */}
         <div className="absolute inset-0 flex justify-center opacity-30 mix-blend-screen pointer-events-none">
            {[...Array(20)].map((_, i) => (
               <div 
                  key={i} 
                  className="w-px bg-cyan-400 absolute bottom-0"
                  style={{
                     left: `${(neuronsMapped / 86) * 100 + (Math.random() * 20 - 10)}%`,
                     height: `${Math.random() * 100}%`,
                     animation: `float-up ${1 + Math.random() * 2}s linear infinite`
                  }}
               ></div>
            ))}
         </div>

      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Neurons Replaced</div>
            <div className={`text-lg font-mono font-bold ${transferComplete ? 'text-cyan-400' : 'text-slate-300'}`}>
               {neuronsMapped.toFixed(1)} <span className="text-xs text-slate-500">Billion</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Connectome Fidelity</div>
            <div className={`text-lg font-mono font-bold ${fidelity > 99.9 ? 'text-emerald-400' : 'text-amber-400'}`}>
               {fidelity.toFixed(3)} <span className="text-xs">%</span>
            </div>
         </div>
      </div>

      <div className="w-full bg-slate-950 rounded border border-slate-800 p-2 text-xs font-mono text-center">
         <span className={transferComplete ? 'text-cyan-400 font-bold' : 'text-slate-400'}>
            {transferComplete ? 'SUBJECTIVE CONTINUITY SECURED' : 'SHIP OF THESEUS PROTOCOL ACTIVE'}
         </span>
      </div>

      <style>{`
        @keyframes float-up {
          0% { transform: translateY(100%); opacity: 1; }
          100% { transform: translateY(-100%); opacity: 0; }
        }
      `}</style>
    </div>
  );
};
