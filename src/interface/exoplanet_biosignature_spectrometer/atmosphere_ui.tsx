import React, { useState, useEffect } from 'react';

export const AtmosphereUi: React.FC = () => {
  const [transitData, setTransitData] = useState<{x: number, y: number}[]>([]);
  const [transitPhase, setTransitPhase] = useState(0); // 0 to 100
  const [hasBiosignature, setHasBiosignature] = useState(false);

  useEffect(() => {
    // Generate the light curve (a dip in brightness as the planet blocks the star)
    const curve = Array.from({length: 100}, (_, i) => {
       const x = i;
       let y = 100; // 100% brightness
       // U-shaped transit dip between 30 and 70
       if (x > 30 && x < 70) {
          // Add noise and atmospheric absorption depth
          y = 99.9 - (Math.sin((x - 30) / 40 * Math.PI) * 0.5) + (Math.random() - 0.5) * 0.05;
       } else {
          y = 100 + (Math.random() - 0.5) * 0.02; // Just stellar noise
       }
       return { x, y };
    });
    setTransitData(curve);

    // Animate the transit phase
    const transit = setInterval(() => {
       setTransitPhase(prev => {
          const next = prev + 1;
          if (next === 50) setHasBiosignature(true); // Mid-transit: detect gases
          if (next >= 100) {
             setHasBiosignature(false);
             return 0;
          }
          return next;
       });
    }, 100);

    return () => clearInterval(transit);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-amber-500">JWST NIRSpec</h2>
          <p className="text-xs text-slate-400">Exoplanet Spectrometer</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-mono border ${hasBiosignature ? 'bg-emerald-900/50 text-emerald-400 border-emerald-800 animate-pulse' : 'bg-slate-800 text-slate-400 border-slate-700'}`}>
          {hasBiosignature ? 'O2 + CH4 DETECTED' : 'SEARCHING...'}
        </div>
      </div>

      {/* Transit Visualizer */}
      <div className="bg-black p-4 rounded border border-slate-800 mb-4 h-[120px] relative overflow-hidden flex items-center justify-center">
         {/* The Star */}
         <div className="w-48 h-48 bg-orange-400/20 rounded-full blur-xl absolute"></div>
         <div className="w-24 h-24 bg-gradient-to-br from-yellow-300 to-orange-600 rounded-full shadow-[0_0_40px_#f59e0b] relative flex items-center justify-center">
            
            {/* The Exoplanet transiting across the star */}
            <div 
               className="absolute w-4 h-4 bg-black rounded-full shadow-[0_0_10px_rgba(0,0,0,0.8)] z-10"
               style={{ left: `${transitPhase}%`, transform: 'translateX(-50%)' }}
            >
               {/* Atmospheric Halo (Blue/Green for Earth-like) */}
               {hasBiosignature && (
                  <div className="absolute inset-0 rounded-full ring-2 ring-cyan-400 blur-[1px]"></div>
               )}
            </div>
         </div>
      </div>
      
      {/* Light Curve Graph */}
      <div className="bg-[#0f172a] p-2 rounded border border-slate-800 mb-4 h-20 relative">
         <div className="absolute top-1 left-1 text-[8px] text-slate-500 font-mono">Relative Flux (%)</div>
         <svg className="w-full h-full" viewBox="0 99.3 100 0.8" preserveAspectRatio="none">
            <polyline 
               fill="none" 
               stroke="#f59e0b" 
               strokeWidth="0.02"
               points={transitData.map(d => `${d.x},${d.y}`).join(' ')} 
            />
            {/* Current Position Marker */}
            <line 
               x1={transitPhase} y1="99.3" x2={transitPhase} y2="100.1" 
               stroke="white" strokeWidth="0.05" opacity="0.5" strokeDasharray="0.1 0.1" 
            />
         </svg>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Target: <span className="text-white">TRAPPIST-1e</span></span>
         <span>ESI (Habitability): <span className="text-emerald-400">0.85</span></span>
      </div>
    </div>
  );
};
