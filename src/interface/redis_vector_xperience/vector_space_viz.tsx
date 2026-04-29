import React, { useState, useEffect } from 'react';

export const VectorSpaceViz: React.FC = () => {
  const [vectors, setVectors] = useState<{x: number, y: number, color: string}[]>([]);

  useEffect(() => {
    // Generate initial cluster of vectors representing a Redis index
    const v = [];
    for(let i=0; i<40; i++) {
        v.push({
            x: 50 + Math.random() * 40,
            y: 50 + Math.random() * 40,
            color: '#ef4444' // Red cluster
        });
        v.push({
            x: 180 + Math.random() * 60,
            y: 80 + Math.random() * 50,
            color: '#3b82f6' // Blue cluster
        });
    }
    setVectors(v);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-red-500">Redis Vector DB</h2>
        <p className="text-xs text-slate-400">Semantic 2D Projection Space</p>
      </div>

      <div className="relative h-48 bg-slate-950 p-2 rounded border border-slate-800 overflow-hidden">
        <svg width="100%" height="100%" viewBox="0 0 300 160">
            {/* Draw vectors */}
            {vectors.map((vec, i) => (
                <circle 
                    key={i} 
                    cx={vec.x} 
                    cy={vec.y} 
                    r={3} 
                    fill={vec.color} 
                    opacity="0.7"
                />
            ))}
            
            {/* Draw a target query vector */}
            <circle cx="160" cy="70" r="5" fill="#10b981" />
            <circle cx="160" cy="70" r="15" fill="none" stroke="#10b981" strokeWidth="1" strokeDasharray="2 2" />
            <text x="170" y="65" fill="#10b981" fontSize="10" fontFamily="monospace">Query</text>
        </svg>
      </div>
      <div className="mt-3 flex justify-between text-[10px] font-mono text-slate-500">
          <span>Index: HNSW</span>
          <span>Distance: L2</span>
      </div>
    </div>
  );
};
