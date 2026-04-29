import React, { useState, useEffect } from 'react';

export const SpatialViz: React.FC = () => {
  const [rotation, setRotation] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setRotation(prev => (prev + 2) % 360);
    }, 50);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-indigo-400">Spatial Reasoning</h2>
        <p className="text-xs text-slate-400">3D Coordinate Engine</p>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 h-[200px] relative flex items-center justify-center overflow-hidden" style={{ perspective: '800px' }}>
         
         {/* Grid Floor */}
         <div 
           className="absolute w-[200px] h-[200px] border border-indigo-900/50"
           style={{ 
             transform: `rotateX(60deg) rotateZ(${rotation}deg)`,
             backgroundImage: 'linear-gradient(to right, rgba(67, 56, 202, 0.2) 1px, transparent 1px), linear-gradient(to bottom, rgba(67, 56, 202, 0.2) 1px, transparent 1px)',
             backgroundSize: '20px 20px'
           }}
         >
             {/* Target Object A (Cup) */}
             <div className="absolute top-[30%] left-[30%] w-4 h-4 bg-rose-500 rounded-full shadow-[0_0_10px_#f43f5e] transform -translate-x-1/2 -translate-y-1/2" style={{ transform: `rotateX(-60deg) rotateY(${-rotation}deg)`}}>
                <div className="absolute -top-4 left-4 text-[8px] bg-slate-900 px-1 rounded border border-slate-700">CUP</div>
             </div>
             
             {/* Target Object B (Table) */}
             <div className="absolute top-[50%] left-[50%] w-24 h-16 border-2 border-indigo-500 bg-indigo-500/20 transform -translate-x-1/2 -translate-y-1/2 flex items-center justify-center">
                 <div className="text-[8px] bg-slate-900 px-1 rounded border border-slate-700 transform" style={{ transform: `rotateX(-60deg) rotateY(${-rotation}deg)`}}>TABLE</div>
             </div>
         </div>
      </div>
      
      <div className="mt-4 p-3 bg-slate-800 rounded border border-slate-700 text-xs text-indigo-300 font-mono">
         LLM Output: "Yes, the <span className="text-rose-400">CUP</span> is physically located on top of the <span className="text-indigo-400">TABLE</span> bounding volume."
      </div>
    </div>
  );
};
