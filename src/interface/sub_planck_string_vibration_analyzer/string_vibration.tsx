import React, { useState, useEffect } from 'react';

export const StringVibration: React.FC = () => {
  const [frequency, setFrequency] = useState(1e42); // Planck frequency
  const [vacuumMetastable, setVacuumMetastable] = useState(false);
  const [dimensions, setDimensions] = useState(4); // Start with 4D spacetime

  useEffect(() => {
    // Simulate zooming into sub-planck scales
    const probe = setInterval(() => {
       if (dimensions < 11) {
          setDimensions(prev => prev + 1);
          setFrequency(prev => prev * 10);
       } else {
          // At 11D, we risk vacuum decay if we push too hard
          if (Math.random() > 0.9) {
             setVacuumMetastable(true);
          }
       }
    }, 1000);

    return () => clearInterval(probe);
  }, [dimensions]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-fuchsia-400">M-Theory</h2>
          <p className="text-xs text-slate-400">Sub-Planck String Analyzer</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-bold border ${vacuumMetastable ? 'bg-red-900/80 text-white border-red-500 shadow-[0_0_15px_#ef4444] animate-pulse' : 'bg-slate-800 text-slate-400 border-slate-700'}`}>
          {vacuumMetastable ? 'FALSE VACUUM DECAY RISK' : 'PROBING METRIC'}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex flex-col items-center justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* The String */}
         <svg className="absolute inset-0 w-full h-full" viewBox="0 0 200 200">
            <path 
               d={`M 20 100 Q 60 ${100 + Math.sin(Date.now() / 100) * 80} 100 100 T 180 100`} 
               fill="none" 
               stroke={vacuumMetastable ? '#ef4444' : '#e879f9'} 
               strokeWidth="2"
               style={{ 
                  filter: 'drop-shadow(0 0 10px #c084fc)',
                  transformOrigin: 'center',
                  animation: `spin ${12 - dimensions}s linear infinite`
               }}
            />
            {dimensions > 6 && (
               <path 
                  d={`M 100 20 Q ${100 + Math.cos(Date.now() / 150) * 80} 60 100 100 T 100 180`} 
                  fill="none" 
                  stroke={vacuumMetastable ? '#ef4444' : '#c084fc'} 
                  strokeWidth="1.5"
                  style={{ 
                     filter: 'drop-shadow(0 0 10px #e879f9)',
                     animation: `spin-reverse ${13 - dimensions}s linear infinite`
                  }}
               />
            )}
            {dimensions > 9 && (
               <circle cx="100" cy="100" r={40 + Math.sin(Date.now()/50)*10} fill="none" stroke="#a855f7" strokeWidth="1" style={{filter: 'drop-shadow(0 0 5px #a855f7)'}} />
            )}
         </svg>

         {/* Calabi-Yau Manifold abstract representation */}
         {dimensions >= 11 && !vacuumMetastable && (
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_transparent_20%,_rgba(192,132,252,0.2)_100%)] animate-pulse"></div>
         )}
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Observable Dimensions</div>
            <div className={`text-lg font-mono font-bold ${dimensions === 11 ? 'text-fuchsia-400' : 'text-slate-400'}`}>
               {dimensions}D <span className="text-[8px] text-slate-500">{dimensions > 4 ? 'Compactified' : 'Spacetime'}</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Vibration Freq</div>
            <div className="text-lg font-mono font-bold text-white">
               10<sup className="text-xs">{Math.log10(frequency).toFixed(0)}</sup> <span className="text-xs text-slate-500">Hz</span>
            </div>
         </div>
      </div>

      <div className="w-full bg-slate-950 rounded border border-slate-800 p-2 text-xs font-mono text-center">
         <span className={vacuumMetastable ? 'text-red-400' : 'text-emerald-400'}>
            {vacuumMetastable ? 'HALT PROBING - METASTABILITY DETECTED' : 'CALABI-YAU GEOMETRY STABLE'}
         </span>
      </div>

      <style>{`
        @keyframes spin { 100% { transform: rotate(360deg); } }
        @keyframes spin-reverse { 100% { transform: rotate(-360deg); } }
      `}</style>
    </div>
  );
};
