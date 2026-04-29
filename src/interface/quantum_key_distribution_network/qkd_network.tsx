import React, { useState, useEffect } from 'react';

export const QkdNetwork: React.FC = () => {
  const [qber, setQber] = useState(0.02);
  const [keyGenerated, setKeyGenerated] = useState(0); // Bits
  const [eveActive, setEveActive] = useState(false);

  useEffect(() => {
    // Simulate BB84 Key Generation
    const qkd = setInterval(() => {
       if (eveActive) {
          // Eve intercepts half the photons, guessing the basis wrong 50% of the time,
          // causing errors for Bob 25% of the time (0.5 * 0.5)
          setQber(prev => Math.min(0.28, prev + 0.05));
       } else {
          setQber(prev => Math.max(0.01, prev - 0.02));
          // Generate secure key if QBER < 11%
          if (qber < 0.11) {
             setKeyGenerated(prev => prev + 256); // Bits per tick
          }
       }
    }, 500);

    return () => clearInterval(qkd);
  }, [eveActive, qber]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-teal-400">Quantum Crypto</h2>
          <p className="text-xs text-slate-400">BB84 QKD Protocol</p>
        </div>
        <button 
           onClick={() => setEveActive(!eveActive)}
           className={`px-3 py-1 font-bold text-[10px] rounded border transition-colors ${eveActive ? 'bg-red-600 text-white border-red-400 shadow-[0_0_10px_#ef4444]' : 'bg-slate-800 text-slate-400 border-slate-600'}`}
        >
           {eveActive ? 'EVE ACTIVE (ATTACK)' : 'SIMULATE EVE'}
        </button>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex flex-col items-center justify-between shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* Alice (Sender) */}
         <div className="w-full flex justify-between items-center px-4 z-10">
            <div className="flex flex-col items-center">
               <div className="w-8 h-8 rounded border-2 border-teal-500 bg-teal-900/50 flex items-center justify-center text-xs font-bold text-teal-400 shadow-[0_0_15px_#14b8a6]">A</div>
               <span className="text-[10px] text-slate-500 mt-1">ALICE</span>
            </div>
            
            {/* Eve (Eavesdropper) */}
            <div className={`flex flex-col items-center transition-all duration-500 ${eveActive ? 'opacity-100 translate-y-4' : 'opacity-20 -translate-y-8'}`}>
               <div className="w-8 h-8 rounded-full border-2 border-red-500 bg-red-900/50 flex items-center justify-center text-xs font-bold text-red-400 shadow-[0_0_15px_#ef4444]">E</div>
               <span className="text-[10px] text-red-500 mt-1">EVE</span>
            </div>

            {/* Bob (Receiver) */}
            <div className="flex flex-col items-center">
               <div className="w-8 h-8 rounded border-2 border-emerald-500 bg-emerald-900/50 flex items-center justify-center text-xs font-bold text-emerald-400 shadow-[0_0_15px_#10b981]">B</div>
               <span className="text-[10px] text-slate-500 mt-1">BOB</span>
            </div>
         </div>

         {/* Fiber Optic Channel */}
         <div className="absolute top-1/2 left-0 right-0 h-px bg-teal-900/50 -translate-y-1/2"></div>
         
         {/* Photons travelling */}
         <div className="absolute top-1/2 left-0 right-0 h-4 -translate-y-1/2 overflow-hidden">
            {[...Array(5)].map((_, i) => (
               <div 
                  key={i} 
                  className={`absolute w-3 h-3 border-2 ${eveActive ? 'border-red-500' : 'border-teal-400'} rounded-full flex items-center justify-center`}
                  style={{ 
                     top: '2px',
                     animation: `travel 2s linear infinite`,
                     animationDelay: `${i * 0.4}s`
                  }}
               >
                  {/* Polarization state (changing randomly) */}
                  <div className="w-full h-px bg-white/80" style={{ transform: `rotate(${Math.random() > 0.5 ? 0 : 45}deg)` }}></div>
               </div>
            ))}
         </div>

         {/* Secure Key Material output */}
         <div className="w-full flex justify-center z-10 opacity-80">
            <div className="text-[8px] font-mono text-emerald-500 break-all w-48 text-center h-4 overflow-hidden">
               {keyGenerated > 0 ? Array.from({length: 32}, () => Math.round(Math.random())).join('') : 'AWAITING KEY...'}
            </div>
         </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Quantum Error (QBER)</div>
            <div className={`text-lg font-mono font-bold ${qber > 0.11 ? 'text-red-400 animate-pulse' : 'text-teal-400'}`}>
               {(qber * 100).toFixed(1)} <span className="text-xs">%</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Secure Key Length</div>
            <div className="text-lg font-mono font-bold text-emerald-400">
               {keyGenerated} <span className="text-xs">Bits</span>
            </div>
         </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded text-center">
         <span className={qber > 0.11 ? 'text-red-400 font-bold' : 'text-slate-400'}>Security: {qber > 0.11 ? 'COMPROMISED' : 'UNBREAKABLE'}</span>
         <span>Limit: <span className="text-white">11% Threshold</span></span>
      </div>

      <style>{`
        @keyframes travel {
          0% { left: 10%; transform: rotate(0deg); }
          45% { left: 45%; }
          55% { left: 55%; }
          100% { left: 90%; transform: rotate(720deg); }
        }
      `}</style>
    </div>
  );
};
