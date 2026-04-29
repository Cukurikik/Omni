import React, { useState, useEffect } from 'react';

export const AlienSyntax: React.FC = () => {
  const [decryptionProgress, setDecryptionProgress] = useState(0);
  const [signalSnr, setSignalSnr] = useState(45.2);
  const [translation, setTranslation] = useState<string>("___ ___ ___");
  const [nodes, setNodes] = useState<{id: number, type: number, delay: number}[]>([]);

  useEffect(() => {
    // Generate complex heptapod-like topological syntax nodes
    setNodes(Array.from({length: 12}, (_, i) => ({
       id: i,
       type: Math.floor(Math.random() * 3), // Different shapes
       delay: Math.random() * 2 // Animation delay
    })));

    // Decryption process
    const decrypt = setInterval(() => {
       setDecryptionProgress(prev => {
          const next = prev + 2;
          if (next > 30 && next < 60) setTranslation("WE ARE...");
          if (next >= 60 && next < 99) setTranslation("WE ARE OFFERING...");
          if (next >= 100) {
             setTranslation("WE ARE OFFERING TECHNOLOGY.");
             clearInterval(decrypt);
             return 100;
          }
          return next;
       });
       setSignalSnr(45.2 + (Math.random() - 0.5) * 5);
    }, 200);

    return () => clearInterval(decrypt);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-lime-400">Xenolinguistics</h2>
          <p className="text-xs text-slate-400">Non-Linear Syntax Decrypter</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-mono border ${decryptionProgress === 100 ? 'bg-lime-900/50 text-lime-400 border-lime-800 shadow-[0_0_10px_#84cc16]' : 'bg-slate-800 text-slate-400 border-slate-700 animate-pulse'}`}>
          {decryptionProgress === 100 ? 'DECRYPTED' : 'ANALYZING...'}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex items-center justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* Deep Space Signal Noise */}
         <div className="absolute inset-0 opacity-10" style={{ backgroundImage: 'radial-gradient(#84cc16 1px, transparent 1px)', backgroundSize: '4px 4px' }}></div>

         {/* Alien Topological Language Structure (Heptapod logogram style) */}
         <div className={`relative w-40 h-40 transition-all duration-1000 ${decryptionProgress === 100 ? 'scale-100 opacity-100' : 'scale-95 opacity-80'}`}>
            <svg viewBox="0 0 100 100" className="w-full h-full drop-shadow-[0_0_10px_#84cc16]">
               {/* Base Ring */}
               <circle cx="50" cy="50" r="35" fill="none" stroke="#84cc16" strokeWidth="4" className="opacity-80" strokeDasharray="10 5" />
               
               {/* Internal Nodes and Connections */}
               {nodes.map((node, i) => {
                  const angle = (i / nodes.length) * Math.PI * 2;
                  const x = 50 + Math.cos(angle) * 35;
                  const y = 50 + Math.sin(angle) * 35;
                  const cx = 50 + Math.cos(angle) * 15;
                  const cy = 50 + Math.sin(angle) * 15;
                  
                  return (
                     <g key={node.id} className="animate-pulse" style={{ animationDuration: '3s', animationDelay: `${node.delay}s` }}>
                        <line x1="50" y1="50" x2={x} y2={y} stroke="#a3e635" strokeWidth="1" opacity="0.5" />
                        {node.type === 0 && <circle cx={cx} cy={cy} r="4" fill="#84cc16" />}
                        {node.type === 1 && <path d={`M${cx-3},${cy-3} L${cx+3},${cy-3} L${cx},${cy+4} Z`} fill="#84cc16" />}
                        {node.type === 2 && <rect x={cx-3} y={cy-3} width="6" height="6" fill="#84cc16" />}
                     </g>
                  );
               })}
               
               {/* Center Hub */}
               <circle cx="50" cy="50" r="8" fill="#4d7c0f" stroke="#84cc16" strokeWidth="2" />
            </svg>
         </div>
      </div>
      
      <div className="bg-slate-950 p-3 rounded border border-slate-800 mb-4 h-16 flex items-center justify-center font-mono text-xs">
         <span className={`transition-all duration-500 ${decryptionProgress === 100 ? 'text-lime-400 drop-shadow-[0_0_5px_#84cc16]' : 'text-slate-500'}`}>
            "{translation}"
         </span>
      </div>

      <div className="space-y-2 mb-4">
         <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400">Heuristic Mapping</span>
            <span className="font-bold font-mono text-white">{decryptionProgress}%</span>
         </div>
         <div className="w-full h-1 bg-slate-800 rounded relative">
            <div className="absolute top-0 bottom-0 left-0 bg-lime-500 transition-all" style={{ width: `${decryptionProgress}%` }}></div>
         </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>SNR: <span className="text-emerald-400">{signalSnr.toFixed(1)} dB</span></span>
         <span>Structure: <span className="text-emerald-400">Non-Linear 3D</span></span>
      </div>
    </div>
  );
};
