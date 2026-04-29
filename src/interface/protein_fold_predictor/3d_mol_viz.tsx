import React, { useState, useEffect } from 'react';

export const ProteinViz: React.FC = () => {
  const [atoms, setAtoms] = useState<{x: number, y: number, r: number}[]>([]);
  
  useEffect(() => {
    // Generate a simple spiraling backbone (Alpha helix simulation)
    const newAtoms = [];
    for(let i=0; i<40; i++) {
        const t = i * 0.4;
        newAtoms.push({
            x: 150 + Math.cos(t) * 40,
            y: 20 + i * 3,
            r: 3 + (Math.sin(t) * 1.5) // depth illusion
        });
    }
    setAtoms(newAtoms);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-amber-400">AlphaFold Evoformer</h2>
        <p className="text-xs text-slate-400">Protein Structure Prediction</p>
      </div>

      <div className="relative h-48 bg-slate-950 p-2 rounded border border-slate-800 flex justify-center items-center overflow-hidden">
        <svg width="100%" height="100%" viewBox="0 0 300 160">
            {/* Draw backbone connections */}
            <polyline 
                fill="none" 
                stroke="#d97706" 
                strokeWidth="2" 
                opacity="0.5"
                points={atoms.map(a => `${a.x},${a.y}`).join(' ')}
            />
            {/* Draw atoms (C-alpha) */}
            {atoms.map((a, i) => (
                <circle 
                    key={i} 
                    cx={a.x} 
                    cy={a.y} 
                    r={a.r} 
                    fill="#fbbf24" 
                    stroke="#b45309"
                    strokeWidth="0.5"
                />
            ))}
        </svg>
      </div>
      <div className="mt-2 text-[10px] text-slate-500 font-mono text-center">
        pLDDT: 92.4% (High Confidence)
      </div>
    </div>
  );
};
