import React, { useState, useEffect } from 'react';

export const VolatilitySurface: React.FC = () => {
  const [time, setTime] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setTime(prev => prev + 0.1);
    }, 100);
    return () => clearInterval(interval);
  }, []);

  // Generate a mock 3D volatility surface grid (Strike vs Time-to-Maturity)
  const grid = [];
  for (let ttm = 1; ttm <= 5; ttm++) {
    for (let strike = 80; strike <= 120; strike += 10) {
      // Smile effect: Vol is higher at extreme strikes (ITM/OTM) and decreases with time
      const vol = 0.2 + (Math.abs(strike - 100) * 0.005) + (1 / (ttm + 1)) * 0.1;
      grid.push({ x: strike, y: ttm, z: vol });
    }
  }

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-pink-500">Black-Scholes</h2>
          <p className="text-xs text-slate-400">Implied Volatility Surface</p>
        </div>
        <div className="text-[10px] font-mono bg-pink-900/30 text-pink-400 border border-pink-800 px-2 py-1 rounded">
          PDE Solved
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 relative h-[200px] flex items-center justify-center overflow-hidden">
         
         {/* Isometric 3D Grid Mockup */}
         <div 
            className="relative w-48 h-48 transition-transform duration-100 ease-linear"
            style={{ 
               transform: `rotateX(60deg) rotateZ(${time * 10}deg)`,
               transformStyle: 'preserve-3d'
            }}
         >
            {/* Base Grid */}
            <div className="absolute inset-0 border border-pink-500/30 grid grid-cols-4 grid-rows-4">
               {[...Array(16)].map((_, i) => <div key={`g${i}`} className="border border-pink-500/30"></div>)}
            </div>

            {/* Volatility Surface Points (Mocked height via Z-translate) */}
            {grid.map((pt, i) => {
               // Normalize coords to grid size (0-100%)
               const top = ((pt.y - 1) / 4) * 100;
               const left = ((pt.x - 80) / 40) * 100;
               // Height (Z) based on Volatility
               const height = pt.z * 200;
               
               return (
                  <div 
                     key={`pt${i}`} 
                     className="absolute w-2 h-2 bg-white rounded-full -ml-1 -mt-1 shadow-[0_0_8px_#ec4899]"
                     style={{
                        top: `${top}%`,
                        left: `${left}%`,
                        transform: `translateZ(${height}px)`
                     }}
                  >
                     {/* Pillar connecting to base */}
                     <div className="w-px bg-pink-500/50 absolute left-1/2 transform -translate-x-1/2 origin-top" style={{ height: `${height}px`, transform: `rotateX(-90deg)` }}></div>
                  </div>
               );
            })}
         </div>
      </div>
      
      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Asset: <span className="text-white">BTC/USD Options</span></span>
         <span>Greeks: <span className="text-emerald-400">Δ Γ Θ ν</span></span>
         <span className="col-span-2 text-pink-400">Smile: <span className="text-slate-500">OOTM Skew Detected</span></span>
      </div>
    </div>
  );
};
