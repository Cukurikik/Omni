import React, { useState, useEffect } from 'react';

export const MatterMorphing: React.FC = () => {
  const [targetShape, setTargetShape] = useState<'sphere' | 'cube' | 'tool'>('sphere');
  const [completion, setCompletion] = useState(100);
  const [particles, setParticles] = useState<{x: number, y: number}[]>([]);

  // Simple layout engine for shapes
  useEffect(() => {
     setCompletion(0);
     const targetParticles = [];
     
     if (targetShape === 'sphere') {
        for(let i=0; i<100; i++) {
           const angle = Math.random() * Math.PI * 2;
           const r = Math.random() * 40;
           targetParticles.push({ x: 50 + Math.cos(angle)*r, y: 50 + Math.sin(angle)*r });
        }
     } else if (targetShape === 'cube') {
        for(let i=0; i<100; i++) {
           targetParticles.push({ x: 25 + Math.random()*50, y: 25 + Math.random()*50 });
        }
     } else {
        // Wrench tool shape
        for(let i=0; i<60; i++) {
           targetParticles.push({ x: 45 + Math.random()*10, y: 20 + Math.random()*60 }); // Handle
        }
        for(let i=0; i<40; i++) {
           const angle = Math.random() * Math.PI;
           targetParticles.push({ x: 50 + Math.cos(angle)*20, y: 20 - Math.sin(angle)*20 }); // Head
        }
     }
     
     // Animate assembly
     let progress = 0;
     const morph = setInterval(() => {
        progress += 5;
        if (progress > 100) {
           clearInterval(morph);
           setCompletion(100);
           return;
        }
        setCompletion(progress);
        
        // Scatter particles if not 100%
        const current = targetParticles.map(p => ({
           x: progress === 100 ? p.x : p.x + (Math.random() - 0.5) * (100 - progress),
           y: progress === 100 ? p.y : p.y + (Math.random() - 0.5) * (100 - progress),
        }));
        setParticles(current);
     }, 50);

  }, [targetShape]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-indigo-400">Programmable Matter</h2>
          <p className="text-xs text-slate-400">Claytronics Lattice</p>
        </div>
        <div className="flex gap-1">
           <button onClick={() => setTargetShape('sphere')} className={`px-2 py-1 text-xs rounded border ${targetShape === 'sphere' ? 'bg-indigo-600 border-indigo-400' : 'bg-slate-800 border-slate-700'}`}>Sphere</button>
           <button onClick={() => setTargetShape('cube')} className={`px-2 py-1 text-xs rounded border ${targetShape === 'cube' ? 'bg-indigo-600 border-indigo-400' : 'bg-slate-800 border-slate-700'}`}>Cube</button>
           <button onClick={() => setTargetShape('tool')} className={`px-2 py-1 text-xs rounded border ${targetShape === 'tool' ? 'bg-indigo-600 border-indigo-400' : 'bg-slate-800 border-slate-700'}`}>Tool</button>
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] flex items-center justify-center relative overflow-hidden">
         {particles.map((p, i) => (
            <div 
               key={i}
               className="absolute w-1 h-1 bg-indigo-400 rounded-sm shadow-[0_0_5px_#818cf8] transition-all duration-75"
               style={{ left: `${p.x}%`, top: `${p.y}%` }}
            ></div>
         ))}
      </div>
      
      <div className="space-y-2 mb-4">
         <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400">Morphogenesis Phase</span>
            <span className="font-bold font-mono text-emerald-400">{completion}%</span>
         </div>
         {/* Assembly Bar */}
         <div className="w-full h-1 bg-slate-800 rounded relative">
            <div className="absolute top-0 bottom-0 left-0 bg-emerald-500 transition-all" style={{ width: `${completion}%` }}></div>
         </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Nanobots: <span className="text-white">1.4 Billion</span></span>
         <span>Latching: <span className="text-emerald-400">Electrostatic</span></span>
      </div>
    </div>
  );
};
