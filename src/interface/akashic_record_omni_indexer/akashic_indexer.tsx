import React, { useState, useEffect } from 'react';

export const AkashicIndexer: React.FC = () => {
  const [indexing, setIndexing] = useState(true);
  const [dataStored, setDataStored] = useState(0); // Googolplex bytes
  const [compressionRatio, setCompressionRatio] = useState(1);
  const [stability, setStability] = useState(100);

  useEffect(() => {
    const indexer = setInterval(() => {
       if (indexing) {
          setDataStored(prev => {
             const next = prev + 10;
             // As we store more, compression gets harder due to entanglement entropy
             setCompressionRatio(1 + (next / 50));
             return next;
          });
       }
    }, 100);

    return () => clearInterval(indexer);
  }, [indexing]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-amber-500">Akashic Records</h2>
          <p className="text-xs text-slate-400">Omniversal Indexer</p>
        </div>
        <button 
           onClick={() => setIndexing(!indexing)}
           className={`px-3 py-1 font-bold text-[10px] rounded border transition-colors ${indexing ? 'bg-amber-900/50 text-amber-400 border-amber-600 shadow-[0_0_15px_#d97706]' : 'bg-slate-800 text-slate-500 border-slate-700'}`}
        >
           {indexing ? 'INDEXING REALITY' : 'INDEXING PAUSED'}
        </button>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex items-center justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)] perspective-[600px]">
         
         {/* Quantum Foam Background */}
         <div className="absolute inset-0 opacity-20" style={{ background: 'url("data:image/svg+xml,%3Csvg viewBox=\'0 0 200 200\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cfilter id=\'noiseFilter\'%3E%3CfeTurbulence type=\'fractalNoise\' baseFrequency=\'0.65\' numOctaves=\'3\' stitchTiles=\'stitch\'/%3E%3C/filter%3E%3Crect width=\'100%25\' height=\'100%25\' filter=\'url(%23noiseFilter)\'/%3E%3C/svg%3E")' }}></div>

         {/* The Index/Book of Life */}
         <div className="relative w-32 h-40 flex items-center justify-center transform preserve-3d group">
            <div className={`absolute w-full h-full border border-amber-500/50 bg-amber-900/20 shadow-[0_0_30px_rgba(245,158,11,0.2)] rounded ${indexing ? 'animate-[spin_4s_linear_infinite]' : ''}`} style={{ transform: 'rotateY(30deg) rotateX(15deg)' }}>
               {/* Holographic pages */}
               {[...Array(5)].map((_, i) => (
                  <div key={i} className="absolute inset-0 border border-amber-400/30 rounded" style={{ transform: `translateZ(${i * 5 - 10}px)` }}></div>
               ))}
               
               {/* Data streams pouring in */}
               {indexing && (
                  <div className="absolute inset-0 overflow-hidden mix-blend-screen">
                     {[...Array(10)].map((_, i) => (
                        <div key={i} className="absolute w-px bg-amber-300" style={{
                           left: `${Math.random() * 100}%`,
                           top: '-100%',
                           height: '50%',
                           boxShadow: '0 0 5px #fcd34d',
                           animation: `fall ${0.5 + Math.random()}s linear infinite`
                        }}></div>
                     ))}
                  </div>
               )}
            </div>
         </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Data Indexed</div>
            <div className="text-lg font-mono font-bold text-amber-400">
               {dataStored.toFixed(0)} <span className="text-[10px] text-slate-500">Googolplex B</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">MERA Compression</div>
            <div className="text-lg font-mono font-bold text-emerald-400">
               {compressionRatio.toFixed(2)}<span className="text-[10px] text-slate-500">x</span>
            </div>
         </div>
      </div>

      <div className="w-full bg-slate-950 rounded border border-slate-800 p-2 text-[10px] font-mono text-center">
         <span className="text-emerald-400">
            {indexing ? 'QUANTUM STATES ETCHED INTO TOPOLOGY' : 'NO-HIDING THEOREM PRESERVED'}
         </span>
      </div>

      <style>{`
        @keyframes fall {
          0% { transform: translateY(0); opacity: 0; }
          50% { opacity: 1; }
          100% { transform: translateY(200px); opacity: 0; }
        }
      `}</style>
    </div>
  );
};
