import React, { useState, useEffect } from 'react';

export const SpaceViz: React.FC = () => {
  const [queryActive, setQueryActive] = useState(false);
  const [points, setPoints] = useState<{id: number, x: number, y: number, sim: number}[]>([]);

  useEffect(() => {
    // Generate random semantic space
    const pts = Array(40).fill(0).map((_, i) => ({
      id: i,
      x: 10 + Math.random() * 80,
      y: 10 + Math.random() * 80,
      sim: 0
    }));
    setPoints(pts);

    const interval = setInterval(() => {
      setQueryActive(true);
      
      const qx = 20 + Math.random() * 60;
      const qy = 20 + Math.random() * 60;

      setPoints(prev => prev.map(p => {
        // Distance proxy for Cosine Similarity
        const dist = Math.sqrt(Math.pow(p.x - qx, 2) + Math.pow(p.y - qy, 2));
        const sim = Math.max(0, 1 - dist / 50);
        return { ...p, sim };
      }));

      setTimeout(() => setQueryActive(false), 800);
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 flex justify-between items-center border-b border-slate-700 pb-3">
        <div>
          <h2 className="text-xl font-bold text-cyan-400">Embedding Index</h2>
          <p className="text-xs text-slate-400">Vector Similarity Search</p>
        </div>
        <div className={`text-[10px] font-mono px-2 py-1 rounded transition-colors ${queryActive ? 'bg-cyan-900/50 text-cyan-400' : 'bg-slate-800 text-slate-500'}`}>
          {queryActive ? 'SEARCHING K=3' : 'IDLE'}
        </div>
      </div>

      <div className="relative w-full aspect-square bg-slate-950 rounded border border-slate-800">
        {points.map(p => {
          const isTop = p.sim > 0.8;
          return (
            <div key={p.id} 
              className={`absolute w-2 h-2 -ml-1 -mt-1 rounded-full transition-all duration-500
                ${isTop ? 'bg-cyan-400 shadow-[0_0_8px_#22d3ee] scale-150' : 'bg-slate-700 scale-100'}
              `}
              style={{left: `${p.x}%`, top: `${p.y}%`, opacity: isTop ? 1 : 0.3}}
            ></div>
          )
        })}
      </div>
      <div className="mt-4 text-xs font-mono text-slate-500 flex justify-between">
         <span>SIMD: AVX-512</span>
         <span>Dim: 1536</span>
      </div>
    </div>
  );
};
