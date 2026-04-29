import React, { useState, useEffect } from 'react';

export const ViewSynthesizer: React.FC = () => {
  const [pixels, setPixels] = useState<number[]>(Array(64).fill(0));

  useEffect(() => {
    // Simulate progressive rendering 
    let step = 0;
    const interval = setInterval(() => {
      setPixels(prev => {
        const next = [...prev];
        // Render 8 pixels at a time
        for(let i=0; i<8; i++) {
          const idx = (step * 8 + i) % 64;
          // Generate a pseudo-image of a sphere in the center
          const x = idx % 8;
          const y = Math.floor(idx / 8);
          const dist = Math.sqrt(Math.pow(x-3.5, 2) + Math.pow(y-3.5, 2));
          
          if (dist < 2.5) {
            next[idx] = 1; // Object
          } else {
            next[idx] = 0.2; // Background
          }
        }
        return next;
      });
      step++;
    }, 150);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 border-b border-slate-700 pb-2">
        <h2 className="text-xl font-bold text-lime-400">NeRF Renderer</h2>
        <p className="text-xs text-slate-400">Novel View Synthesis</p>
      </div>

      <div className="flex justify-center mb-4">
        <div className="grid grid-cols-8 gap-1 bg-slate-950 p-2 rounded border border-slate-800">
          {pixels.map((val, i) => (
             <div key={i} className="w-6 h-6 rounded-sm transition-colors duration-200" 
                  style={{
                    backgroundColor: val === 0 ? '#0f172a' : 
                                     val === 1 ? '#a3e635' : '#334155'
                  }}>
             </div>
          ))}
        </div>
      </div>

      <div className="flex justify-between items-center text-[10px] text-slate-500 font-bold uppercase tracking-widest">
         <span>Rays/sec: 4.2M</span>
         <span className="text-lime-500 animate-pulse">Rendering...</span>
      </div>
    </div>
  );
};
