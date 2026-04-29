import React, { useState, useEffect } from 'react';

export const GenomeIde: React.FC = () => {
  const [sequence, setSequence] = useState<string[]>([]);
  const bases = ['A', 'C', 'T', 'G'];

  useEffect(() => {
    // Generate an initial random sequence
    setSequence(Array.from({length: 40}, () => bases[Math.floor(Math.random() * 4)]));

    // Simulate the synthesizer "printing" DNA one base at a time
    const print = setInterval(() => {
       setSequence(prev => {
          const next = [...prev];
          next.shift();
          next.push(bases[Math.floor(Math.random() * 4)]);
          return next;
       });
    }, 200);

    return () => clearInterval(print);
  }, []);

  const getBaseColor = (base: string) => {
     switch(base) {
        case 'A': return 'text-red-400 border-red-900/50 bg-red-950/30';
        case 'T': return 'text-yellow-400 border-yellow-900/50 bg-yellow-950/30';
        case 'C': return 'text-blue-400 border-blue-900/50 bg-blue-950/30';
        case 'G': return 'text-emerald-400 border-emerald-900/50 bg-emerald-950/30';
        default: return 'text-white';
     }
  };

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-emerald-400">Synthetic Genome IDE</h2>
          <p className="text-xs text-slate-400">Microfluidic DNA Printing</p>
        </div>
        <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_#10b981] animate-pulse"></div>
      </div>

      {/* DNA Sequence Visualizer */}
      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 font-mono text-sm overflow-hidden relative">
         <div className="absolute top-2 left-2 text-[8px] text-slate-500">5' to 3' SYNTHESIS</div>
         
         <div className="flex flex-wrap gap-1 mt-4">
            {sequence.map((base, i) => (
               <div 
                  key={i} 
                  className={`w-5 h-6 flex items-center justify-center rounded border ${getBaseColor(base)} ${i === 39 ? 'animate-pulse ring-2 ring-white/50' : ''}`}
               >
                  {base}
               </div>
            ))}
         </div>
      </div>
      
      <div className="space-y-2 mb-4">
         <div className="w-full bg-slate-800 border border-slate-700 p-2 rounded flex justify-between items-center text-xs font-mono">
            <span className="text-slate-400">Biosecurity Screen</span>
            <span className="text-emerald-400 font-bold">CLEARED</span>
         </div>
         <div className="w-full bg-slate-800 border border-slate-700 p-2 rounded flex justify-between items-center text-xs font-mono">
            <span className="text-slate-400">CRISPR Off-Target Risk</span>
            <span className="text-emerald-400 font-bold">0.02%</span>
         </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Target: <span className="text-white">Plasmid pUC19</span></span>
         <span>Print Speed: <span className="text-sky-400">12 bp/sec</span></span>
      </div>
    </div>
  );
};
