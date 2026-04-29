import React, { useState, useEffect } from 'react';

export const TopologyViz: React.FC = () => {
  const [scale, setScale] = useState(1e-20); // Zoom level
  const [foamActive, setFoamActive] = useState(false);
  const [wormholes, setWormholes] = useState<{id: number, x1: number, y1: number, x2: number, y2: number}[]>([]);

  useEffect(() => {
    // Zooming into the Planck scale
    if (foamActive && scale > 1e-35) {
       const zoom = setInterval(() => {
          setScale(prev => Math.max(1e-35, prev / 10));
       }, 200);
       return () => clearInterval(zoom);
    } else if (!foamActive && scale < 1e-20) {
       const unzoom = setInterval(() => {
          setScale(prev => Math.min(1e-20, prev * 10));
       }, 200);
       return () => clearInterval(unzoom);
    }
  }, [foamActive, scale]);

  useEffect(() => {
     // At Planck scale, spacetime boils (Quantum Foam)
     if (scale <= 1e-32) {
        const churn = setInterval(() => {
           // Generate random transient wormhole connections
           const newWormholes = Array.from({length: 8}, (_, i) => ({
              id: Date.now() + i,
              x1: Math.random() * 100,
              y1: Math.random() * 100,
              x2: Math.random() * 100,
              y2: Math.random() * 100
           }));
           setWormholes(newWormholes);
        }, 150);
        return () => clearInterval(churn);
     } else {
        setWormholes([]); // Smooth spacetime at macro scales
     }
  }, [scale]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-fuchsia-400">Quantum Foam</h2>
          <p className="text-xs text-slate-400">Spacetime Topology</p>
        </div>
        <button 
           onClick={() => setFoamActive(!foamActive)}
           className={`px-3 py-1 font-bold text-[10px] rounded border transition-colors ${foamActive ? 'bg-fuchsia-600 text-white border-fuchsia-400 shadow-[0_0_10px_#c026d3]' : 'bg-slate-800 text-slate-400 border-slate-600'}`}
        >
           {foamActive ? 'MACRO-SCALE' : 'ZOOM PLANCK'}
        </button>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex items-center justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* Spacetime Grid */}
         <div 
            className="absolute inset-0 transition-transform duration-1000"
            style={{ 
               backgroundImage: `linear-gradient(rgba(192, 38, 211, ${scale <= 1e-32 ? 0.1 : 0.3}) 1px, transparent 1px), linear-gradient(90deg, rgba(192, 38, 211, ${scale <= 1e-32 ? 0.1 : 0.3}) 1px, transparent 1px)`,
               backgroundSize: scale <= 1e-32 ? '10px 10px' : '40px 40px',
               // Distort grid heavily at Planck scale
               filter: scale <= 1e-32 ? 'url(#turbulence)' : 'none'
            }}
         ></div>

         {/* SVG Filters for quantum boiling effect */}
         <svg className="hidden">
            <defs>
               <filter id="turbulence">
                  <feTurbulence type="fractalNoise" baseFrequency="0.05" numOctaves="2" result="noise" />
                  <feDisplacementMap in="SourceGraphic" in2="noise" scale="20" xChannelSelector="R" yChannelSelector="G" />
               </filter>
            </defs>
         </svg>

         {/* Transient Wormholes */}
         <svg className="absolute inset-0 w-full h-full">
            {wormholes.map(w => (
               <g key={w.id}>
                  {/* Wormhole Mouths */}
                  <circle cx={`${w.x1}%`} cy={`${w.y1}%`} r="3" fill="#e879f9" className="animate-pulse" />
                  <circle cx={`${w.x2}%`} cy={`${w.y2}%`} r="3" fill="#e879f9" className="animate-pulse" />
                  {/* The Throat (Connecting distant points instantly) */}
                  <path 
                     d={`M ${w.x1*3.5} ${w.y1*2} Q 150 100 ${w.x2*3.5} ${w.y2*2}`} 
                     fill="none" 
                     stroke="rgba(232, 121, 249, 0.4)" 
                     strokeWidth="1.5" 
                     className="animate-[dash_0.1s_linear_forwards]"
                     strokeDasharray="5 5"
                  />
               </g>
            ))}
         </svg>
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Scale (Zoom)</div>
            <div className={`text-lg font-mono font-bold ${scale <= 1e-35 ? 'text-fuchsia-400' : 'text-slate-300'}`}>
               10<sup className="text-xs">{Math.log10(scale)}</sup> <span className="text-xs">m</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Topology</div>
            <div className={`text-lg font-mono font-bold ${scale <= 1e-32 ? 'text-red-400' : 'text-emerald-400'}`}>
               {scale <= 1e-32 ? 'MULTIPLY CONNECTED' : 'EUCLIDEAN FLAT'}
            </div>
         </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Stabilizer: <span className="text-white">Casimir Negative E</span></span>
         <span>Payload: <span className="text-emerald-400">Entangled Photons</span></span>
      </div>
    </div>
  );
};
