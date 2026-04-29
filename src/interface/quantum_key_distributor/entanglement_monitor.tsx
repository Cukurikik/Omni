import React, { useState, useEffect } from 'react';

export const EntanglementMonitor: React.FC = () => {
  const [photons, setPhotons] = useState<{id: number, basis: string, bit: number}[]>([]);
  const [qber, setQber] = useState(2.1); // Quantum Bit Error Rate

  useEffect(() => {
    // Generate streaming quantum bits
    const interval = setInterval(() => {
      setPhotons(prev => {
         const next = [...prev];
         if (next.length > 8) next.shift();
         
         const basis = Math.random() > 0.5 ? '+' : '×';
         const bit = Math.random() > 0.5 ? 1 : 0;
         
         next.push({ id: Date.now(), basis, bit });
         return next;
      });

      // Fluctuate QBER slightly
      setQber(prev => Math.max(0.5, Math.min(10, prev + (Math.random() - 0.5) * 0.5)));

    }, 300);

    return () => clearInterval(interval);
  }, []);

  const isSecure = qber < 5.0; // Theoretical threshold

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-indigo-400">Quantum Network</h2>
          <p className="text-xs text-slate-400">BB84 QKD Protocol</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-mono border ${isSecure ? 'bg-emerald-900/30 text-emerald-400 border-emerald-800' : 'bg-red-900/50 text-red-400 border-red-800 animate-pulse'}`}>
          {isSecure ? 'SECURE' : 'EAVESDROPPER DETECTED'}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 font-mono text-xs overflow-hidden h-[120px] relative">
         
         {/* Photon Stream Visualizer */}
         <div className="flex items-center h-full space-x-2 absolute right-4">
            {photons.map((p) => (
               <div 
                  key={p.id} 
                  className="flex flex-col items-center justify-center animate-[slide_3s_linear_infinite]"
                  style={{ animationName: 'slide-left' }}
               >
                  {/* Polarization vector visual */}
                  <div className={`w-6 h-6 border border-slate-700 rounded-full flex items-center justify-center mb-1 ${p.basis === '+' ? 'text-sky-400' : 'text-fuchsia-400'}`}>
                     {p.basis === '+' ? (p.bit === 1 ? '↑' : '→') : (p.bit === 1 ? '↗' : '↘')}
                  </div>
                  <span className="text-white font-bold">{p.bit}</span>
               </div>
            ))}
         </div>

      </div>
      
      <div className="space-y-2 mb-4">
         <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400">Quantum Bit Error Rate (QBER)</span>
            <span className={`font-bold font-mono ${isSecure ? 'text-emerald-400' : 'text-red-400'}`}>{qber.toFixed(2)}%</span>
         </div>
         {/* Warning bar */}
         <div className="w-full h-1 bg-slate-800 rounded relative">
            <div className={`absolute top-0 bottom-0 left-0 transition-all ${isSecure ? 'bg-emerald-500' : 'bg-red-500'}`} style={{ width: `${(qber / 10) * 100}%` }}></div>
            <div className="absolute top-0 bottom-0 w-px bg-red-500 z-10" style={{ left: '50%' }}></div>
         </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Sifting: <span className="text-emerald-400">Base Match 50%</span></span>
         <span>Rate: <span className="text-white">100 kbits/s</span></span>
      </div>

      <style>{`
        @keyframes slide-left {
          from { transform: translateX(50px); opacity: 0; }
          to { transform: translateX(-250px); opacity: 1; }
        }
      `}</style>
    </div>
  );
};
