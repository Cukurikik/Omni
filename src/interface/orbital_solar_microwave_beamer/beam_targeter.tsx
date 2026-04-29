import React, { useState, useEffect } from 'react';

export const BeamTargeter: React.FC = () => {
  const [beamX, setBeamX] = useState(50);
  const [beamY, setBeamY] = useState(50);
  const [power, setPower] = useState(0.85); // Gigawatts
  const [focused, setFocused] = useState(false);

  useEffect(() => {
    // Retrodirective phase conjugation hunting for the target
    const target = setInterval(() => {
      setBeamX(prev => {
         const diff = 50 - prev;
         return prev + diff * 0.2 + (Math.random() - 0.5) * 2;
      });
      setBeamY(prev => {
         const diff = 50 - prev;
         return prev + diff * 0.2 + (Math.random() - 0.5) * 2;
      });
    }, 100);

    return () => clearInterval(target);
  }, []);

  useEffect(() => {
     // Check if beam is focused on target (center)
     const dist = Math.sqrt(Math.pow(beamX - 50, 2) + Math.pow(beamY - 50, 2));
     setFocused(dist < 5);
     
     if (dist < 5) {
        setPower(prev => Math.min(1.0, prev + 0.05));
     } else {
        setPower(prev => Math.max(0.1, prev - 0.1)); // Defocus drops power transfer
     }
  }, [beamX, beamY]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-yellow-400">Space Solar Power</h2>
          <p className="text-xs text-slate-400">Orbital Microwave Beamer</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-mono border ${focused ? 'bg-yellow-900/50 text-yellow-400 border-yellow-800' : 'bg-red-900/50 text-red-400 border-red-800 animate-pulse'}`}>
          {focused ? 'PHASE LOCKED' : 'HUNTING PILOT'}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[180px] flex items-center justify-center relative overflow-hidden">
         
         {/* Ground Map Grid */}
         <div className="absolute inset-0 opacity-20 grid grid-cols-6 grid-rows-6">
            {[...Array(36)].map((_, i) => <div key={i} className="border border-green-500/30"></div>)}
         </div>

         {/* The Rectenna Target Area (Center) */}
         <div className="w-12 h-12 rounded-full border-2 border-green-500 border-dashed absolute z-0 flex items-center justify-center">
            <div className="w-1 h-1 bg-green-500 rounded-full"></div>
         </div>

         {/* The Microwave Beam Hitbox */}
         <div 
            className={`absolute rounded-full transition-all duration-75 blur-md ${focused ? 'bg-yellow-400' : 'bg-red-500'}`}
            style={{ 
               left: `calc(${beamX}% - ${focused ? '24px' : '48px'})`, 
               top: `calc(${beamY}% - ${focused ? '24px' : '48px'})`,
               width: focused ? '48px' : '96px', // Beam is tight when focused, scattered when not
               height: focused ? '48px' : '96px',
               opacity: focused ? 0.8 : 0.4,
               boxShadow: `0 0 ${focused ? '30px #facc15' : '15px #ef4444'}`
            }}
         ></div>
      </div>
      
      <div className="space-y-2 mb-4">
         <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400">Ground Rectenna Yield</span>
            <span className={`font-bold font-mono ${focused ? 'text-yellow-400' : 'text-slate-400'}`}>
               {(power * 1000).toFixed(0)} MW
            </span>
         </div>
         {/* Power Transfer Bar */}
         <div className="w-full h-2 bg-slate-800 rounded relative overflow-hidden">
            <div className={`absolute top-0 bottom-0 left-0 transition-all ${focused ? 'bg-yellow-500' : 'bg-slate-500'}`} style={{ width: `${power * 100}%` }}></div>
         </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Freq: <span className="text-white">2.45 GHz ISM</span></span>
         <span>Aviation: <span className="text-emerald-400">Clear</span></span>
      </div>
    </div>
  );
};
