import React, { useState, useEffect } from 'react';

export const MeshViewer: React.FC = () => {
  const [rotation, setRotation] = useState(0);
  const [expression, setExpression] = useState(0);

  useEffect(() => {
    let t = 0;
    const interval = setInterval(() => {
      t++;
      // Deterministic autonomous 3D face rotation and expression animation
      setRotation(t * 0.05);
      
      // Mouth opening expression (sinusoidal)
      setExpression(Math.max(0, Math.sin(t * 0.1)));
    }, 50);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg shadow-2xl border border-slate-700 max-w-lg mx-auto font-sans">
      <div className="mb-4 border-b border-slate-800 pb-4">
        <h2 className="text-xl font-bold text-teal-400">3D Morphable Model</h2>
        <p className="text-xs text-slate-500">EOS Fit Projection</p>
      </div>

      <div className="relative aspect-square bg-slate-950 border border-slate-800 rounded overflow-hidden flex items-center justify-center perspective-1000">
        
        {/* Wireframe Mesh Container */}
        <div 
          className="relative w-48 h-48 transition-transform duration-75"
          style={{ transform: `rotateY(${rotation}rad)` }}
        >
          {/* Simulated Face Bounds */}
          <div className="absolute inset-0 border-[0.5px] border-teal-500/20 rounded-[40%_40%_50%_50%]"></div>
          
          {/* Left Eye */}
          <div className="absolute top-16 left-8 w-6 h-3 border-[0.5px] border-teal-400/50 rounded-full"></div>
          {/* Right Eye */}
          <div className="absolute top-16 right-8 w-6 h-3 border-[0.5px] border-teal-400/50 rounded-full"></div>
          
          {/* Nose */}
          <div className="absolute top-20 left-1/2 -translate-x-1/2 w-4 h-10 border-b-[0.5px] border-r-[0.5px] border-teal-500/40"></div>
          
          {/* Mouth (animated via blendshape expression math) */}
          <div 
            className="absolute bottom-12 left-1/2 -translate-x-1/2 border-[0.5px] border-teal-400/60 rounded-full transition-all duration-75"
            style={{ 
              width: '40px', 
              height: `${4 + expression * 16}px` 
            }}
          ></div>
        </div>

      </div>

      <div className="mt-4 grid grid-cols-2 gap-4">
        <div className="bg-slate-800 p-2 rounded text-center">
          <div className="text-[10px] text-slate-400">ALPHA (SHAPE)</div>
          <div className="font-mono text-sm text-teal-300">PCA L2 Solved</div>
        </div>
        <div className="bg-slate-800 p-2 rounded text-center">
          <div className="text-[10px] text-slate-400">EXPRESSION (BLEND)</div>
          <div className="font-mono text-sm text-teal-300">{expression.toFixed(2)}</div>
        </div>
      </div>
    </div>
  );
};
