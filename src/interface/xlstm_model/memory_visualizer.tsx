import React, { useState, useEffect } from 'react';

export const MemoryVisualizer: React.FC = () => {
  const [matrix, setMatrix] = useState<number[][]>(Array(8).fill(Array(8).fill(0)));

  useEffect(() => {
    let t = 0;
    const interval = setInterval(() => {
      t++;
      
      // Deterministic xLSTM memory state rendering
      const newMatrix = Array.from({ length: 8 }, (_, i) => 
        Array.from({ length: 8 }, (_, j) => {
          // Exponential gating math simulation
          const val = Math.sin(t * 0.1 + i) * Math.cos(t * 0.1 + j) + 1; // 0 to 2
          return val > 1.8 ? 1 : val * 0.5; 
        })
      );
      
      setMatrix(newMatrix);
    }, 150);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-neutral-900 p-8 rounded-xl shadow-2xl w-full max-w-md font-mono text-neutral-200 border border-neutral-700 mx-auto">
      <div className="mb-6 flex justify-between items-center">
        <h2 className="text-xl font-bold text-[#ff007f] tracking-widest">xLSTM Covariance</h2>
        <span className="text-xs bg-neutral-800 px-2 py-1 border border-neutral-600 rounded">DIM: 8x8</span>
      </div>

      <div className="grid grid-cols-8 gap-1 p-2 bg-neutral-950 rounded border border-neutral-800">
        {matrix.map((row, i) => 
          row.map((cell, j) => {
            // Color map for memory activations
            const r = Math.floor(cell * 255);
            const b = Math.floor((1 - cell) * 100);
            
            return (
              <div 
                key={`${i}-${j}`} 
                className="w-full aspect-square rounded-sm transition-colors duration-150"
                style={{ 
                  backgroundColor: `rgb(${r}, 0, ${b})`,
                  boxShadow: cell > 0.8 ? `0 0 8px rgba(255, 0, 127, 0.6)` : 'none'
                }}
              />
            );
          })
        )}
      </div>

      <div className="mt-6 text-xs text-neutral-500 flex justify-between">
        <span>Forget Gate [0.0]</span>
        <span>Exponential Gate [1.0+]</span>
      </div>
    </div>
  );
};
