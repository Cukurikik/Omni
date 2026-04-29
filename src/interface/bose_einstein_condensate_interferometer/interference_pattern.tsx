import React, { useState, useEffect } from 'react';

export const InterferencePattern: React.FC = () => {
  const [fringeShift, setFringeShift] = useState(0);
  const [tempNk, setTempNk] = useState(150);
  const [waveDetected, setWaveDetected] = useState(false);

  useEffect(() => {
    // Simulate Gravity Wave event
    const event = setInterval(() => {
      const isWave = Math.random() > 0.9;
      if (isWave) {
         setWaveDetected(true);
         setFringeShift(Math.PI / 2); // Sudden phase shift
         setTimeout(() => {
            setWaveDetected(false);
            setFringeShift(0);
         }, 3000);
      }
      
      // Minor thermal fluctuations
      if (!isWave) {
         setFringeShift(prev => prev + (Math.random() - 0.5) * 0.1);
      }
    }, 2000);

    return () => clearInterval(event);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-sky-400">BEC Interferometer</h2>
          <p className="text-xs text-slate-400">Quantum Gravity Sensor</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-mono border ${waveDetected ? 'bg-sky-900/50 text-sky-400 border-sky-800 animate-pulse' : 'bg-slate-800 text-slate-400 border-slate-700'}`}>
          {waveDetected ? 'SPACETIME RIPPLE' : 'SENSING'}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[180px] flex flex-col items-center justify-center relative overflow-hidden">
         
         {/* Absorption Imaging Visualization (Interference Fringes) */}
         <div className="w-full h-full relative flex flex-col items-center justify-center filter contrast-125">
            {[...Array(20)].map((_, i) => {
               // Calculate sine wave intensity for fringes
               const phase = (i / 20) * Math.PI * 4 + fringeShift;
               const intensity = (Math.sin(phase) + 1) / 2; // 0 to 1
               
               // Gaussian envelope (center is brightest)
               const envelope = Math.exp(-Math.pow((i - 10) / 5, 2));
               
               const finalOpacity = intensity * envelope;
               
               return (
                  <div 
                     key={i}
                     className="w-4/5 h-2 bg-sky-500 rounded-full transition-all duration-300"
                     style={{ opacity: finalOpacity, transform: `scaleX(${envelope})` }}
                  ></div>
               )
            })}
         </div>

         {/* Target Reticle */}
         <div className="absolute inset-0 flex items-center justify-center opacity-30 pointer-events-none">
            <div className="w-32 h-32 border border-sky-400 rounded-full"></div>
            <div className="w-full h-px bg-sky-400 absolute"></div>
            <div className="h-full w-px bg-sky-400 absolute"></div>
         </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4 text-center">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Gravity (g)</div>
            <div className="text-lg font-mono font-bold text-white">9.80665<span className="text-sky-400 text-sm">{waveDetected ? '4' : '0'}</span></div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Phase Shift</div>
            <div className={`text-lg font-mono font-bold ${waveDetected ? 'text-sky-400' : 'text-slate-500'}`}>
               {fringeShift.toFixed(2)} <span className="text-xs">rad</span>
            </div>
         </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Atoms: <span className="text-white">Rubidium-87</span></span>
         <span>Temp: <span className="text-sky-400">{tempNk} nK</span></span>
      </div>
    </div>
  );
};
