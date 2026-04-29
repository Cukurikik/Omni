import React, { useState, useEffect } from 'react';

export const EntropyReversalUi: React.FC = () => {
  const [timeDirection, setTimeDirection] = useState<'FORWARD' | 'REVERSE'>('FORWARD');
  const [entropy, setEntropy] = useState(0); // 0 = Ordered, 100 = Chaotic
  const [particles, setParticles] = useState<{x: number, y: number, vx: number, vy: number}[]>([]);

  // Initialize ordered state
  useEffect(() => {
     const initial = [];
     // Start as a perfectly ordered block in the center
     for(let i=0; i<10; i++) {
        for(let j=0; j<10; j++) {
           initial.push({
              x: 45 + i,
              y: 45 + j,
              vx: (Math.random() - 0.5) * 2,
              vy: (Math.random() - 0.5) * 2
           });
        }
     }
     setParticles(initial);
  }, []);

  useEffect(() => {
    // Thermodynamics simulation
    const physics = setInterval(() => {
       setParticles(prev => prev.map(p => {
          let nx = p.x + (timeDirection === 'FORWARD' ? p.vx : -p.vx);
          let ny = p.y + (timeDirection === 'FORWARD' ? p.vy : -p.vy);
          
          // Bounce off walls (imperfectly to simulate slight decoherence over long times, 
          // but for this short viz we keep it reversible)
          if (nx <= 0 || nx >= 100) p.vx *= -1;
          if (ny <= 0 || ny >= 100) p.vy *= -1;
          
          nx = Math.max(0, Math.min(100, nx));
          ny = Math.max(0, Math.min(100, ny));
          
          return { ...p, x: nx, y: ny };
       }));
       
       // Calculate approximate entropy (spread)
       setEntropy(prev => {
          if (timeDirection === 'FORWARD') return Math.min(100, prev + 1);
          return Math.max(0, prev - 1);
       });
       
    }, 50);

    return () => clearInterval(physics);
  }, [timeDirection]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-violet-400">Entropy Reverser</h2>
          <p className="text-xs text-slate-400">Loschmidt Echo Chamber</p>
        </div>
        <button 
           onClick={() => setTimeDirection(d => d === 'FORWARD' ? 'REVERSE' : 'FORWARD')}
           className={`px-3 py-1 font-bold text-[10px] rounded border transition-colors ${timeDirection === 'REVERSE' ? 'bg-violet-600 text-white border-violet-400 shadow-[0_0_10px_#8b5cf6]' : 'bg-slate-800 text-slate-400 border-slate-600'}`}
        >
           {timeDirection === 'REVERSE' ? 'INVERT HAMILTONIAN' : 'NORMAL TIME'}
        </button>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex items-center justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* Temporal Distortion Effect */}
         {timeDirection === 'REVERSE' && (
            <div className="absolute inset-0 bg-violet-500/10 animate-pulse mix-blend-screen pointer-events-none"></div>
         )}

         {/* Particles */}
         {particles.map((p, i) => (
            <div 
               key={i}
               className={`absolute w-1 h-1 rounded-full transition-all duration-75 ${timeDirection === 'REVERSE' ? 'bg-violet-400 shadow-[0_0_5px_#a78bfa]' : 'bg-orange-400'}`}
               style={{ left: `${p.x}%`, top: `${p.y}%` }}
            ></div>
         ))}
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800 relative overflow-hidden">
            <div className="text-[10px] uppercase text-slate-500 mb-1 relative z-10">System Entropy (S)</div>
            <div className="text-lg font-mono font-bold text-white relative z-10">{entropy.toFixed(1)} <span className="text-xs text-slate-500">J/K</span></div>
            <div className={`absolute bottom-0 left-0 right-0 opacity-20 ${timeDirection === 'REVERSE' ? 'bg-violet-500' : 'bg-orange-500'}`} style={{ height: `${entropy}%` }}></div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Time Arrow</div>
            <div className={`text-lg font-mono font-bold ${timeDirection === 'REVERSE' ? 'text-violet-400 animate-pulse' : 'text-slate-400'}`}>
               {timeDirection === 'FORWARD' ? 't > 0' : 't < 0 (REVERSING)'}
            </div>
         </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Fidelity: <span className="text-emerald-400">0.99999</span></span>
         <span>CTC: <span className={entropy === 0 ? 'text-emerald-400' : 'text-slate-500'}>{entropy === 0 ? 'STABLE LOOP' : 'Open'}</span></span>
      </div>
    </div>
  );
};
