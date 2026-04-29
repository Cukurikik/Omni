import React, { useState, useEffect } from 'react';

export const LaserInterference: React.FC = () => {
  const [phase, setPhase] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate dynamic MZI phase shifting
      setPhase(p => (p + 0.1) % (Math.PI * 2));
    }, 50);
    return () => clearInterval(interval);
  }, []);

  // Compute Mach-Zehnder interference intensities
  const topIntensity = Math.sin(phase / 2) ** 2;
  const bottomIntensity = Math.cos(phase / 2) ** 2;

  // Convert to RGBA for laser visual
  const topColor = `rgba(239, 68, 68, ${topIntensity})`;     // Red laser
  const bottomColor = `rgba(239, 68, 68, ${bottomIntensity})`;

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-rose-500">Photonic ALU</h2>
          <p className="text-xs text-slate-400">Mach-Zehnder Interferometer</p>
        </div>
        <div className="px-2 py-1 bg-slate-800 text-rose-400 text-[10px] font-mono rounded border border-rose-900/50 flex items-center gap-1">
          <div className="w-1.5 h-1.5 bg-rose-500 rounded-full animate-pulse"></div> Light-Speed
        </div>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 h-[140px] relative flex items-center justify-center mb-4">
         
         <div className="relative w-full h-full flex items-center justify-between px-4">
            
            {/* Input Laser (Constant) */}
            <div className="w-1/4 h-1 bg-rose-500 shadow-[0_0_8px_#ef4444]"></div>
            
            {/* Beam Splitter 1 */}
            <div className="w-2 h-12 bg-slate-400/50 transform rotate-45 border border-slate-300"></div>
            
            {/* Phase Shifters (Top/Bottom paths) */}
            <div className="flex flex-col justify-between h-16 w-1/4">
               {/* Top Path */}
               <div className="w-full h-1 relative">
                  <div className="absolute inset-0 bg-rose-500 shadow-[0_0_8px_#ef4444]"></div>
                  {/* Heater/Phase Modulator */}
                  <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-6 h-3 bg-amber-500/80 rounded border border-amber-400"></div>
               </div>
               {/* Bottom Path */}
               <div className="w-full h-1 bg-rose-500 shadow-[0_0_8px_#ef4444]"></div>
            </div>

            {/* Beam Splitter 2 */}
            <div className="w-2 h-12 bg-slate-400/50 transform -rotate-45 border border-slate-300"></div>

            {/* Output Lasers (Interfered) */}
            <div className="flex flex-col justify-between h-16 w-1/4">
               <div className="w-full h-1 transition-all duration-75" style={{ backgroundColor: topColor, boxShadow: `0 0 8px ${topColor}` }}></div>
               <div className="w-full h-1 transition-all duration-75" style={{ backgroundColor: bottomColor, boxShadow: `0 0 8px ${bottomColor}` }}></div>
            </div>

         </div>

      </div>
      
      <div className="flex justify-between text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Phase: {(phase * (180/Math.PI)).toFixed(0)}°</span>
         <span>Out 1: {(topIntensity * 100).toFixed(0)}%</span>
         <span>Out 2: {(bottomIntensity * 100).toFixed(0)}%</span>
      </div>
    </div>
  );
};
