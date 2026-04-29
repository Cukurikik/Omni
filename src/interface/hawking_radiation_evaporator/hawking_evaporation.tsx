import React, { useState, useEffect } from 'react';

export const HawkingEvaporation: React.FC = () => {
  const [bhMass, setBhMass] = useState(1.5e8); // 150,000 tons
  const [temperature, setTemperature] = useState(0);
  const [powerOutput, setPowerOutput] = useState(0);
  const [critical, setCritical] = useState(false);

  useEffect(() => {
    // Simulate Black Hole evaporation (accelerates as mass decreases)
    const evaporate = setInterval(() => {
       setBhMass(prev => {
          // Mass loss rate is inversely proportional to mass squared (simplified)
          const loss = 1e16 / Math.pow(prev, 2);
          const next = prev - loss;
          
          if (next < 1.0e8) setCritical(true);
          else setCritical(false);
          
          // Terminal flash check
          if (next <= 0) {
             clearInterval(evaporate);
             return 0; 
          }
          return next;
       });
    }, 100);

    return () => clearInterval(evaporate);
  }, []);

  useEffect(() => {
     // Temp is inversely proportional to mass
     if (bhMass > 0) {
        const temp = 1.227e23 / bhMass; 
        setTemperature(temp);
        
        // Power is proportional to T^4 (Stefan-Boltzmann) * Area
        // Area is proportional to M^2. So Power ~ 1/M^2
        const power = 3.56e32 / Math.pow(bhMass, 2);
        setPowerOutput(power);
     }
  }, [bhMass]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-orange-500">Hawking Reactor</h2>
          <p className="text-xs text-slate-400">Micro-Singularity Grid</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-mono border ${critical ? 'bg-red-900/50 text-red-400 border-red-800 animate-pulse shadow-[0_0_15px_#ef4444]' : 'bg-slate-800 text-slate-400 border-slate-700'}`}>
          {critical ? 'INJECT MATTER NOW' : 'STABLE YIELD'}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex items-center justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* Hawking Radiation Emission */}
         <div className="absolute inset-0 flex items-center justify-center">
            {[...Array(24)].map((_, i) => (
               <div 
                  key={i} 
                  className={`absolute w-full h-px ${critical ? 'bg-orange-500/80' : 'bg-sky-500/40'}`} 
                  style={{ 
                     transform: `rotate(${i * 15}deg)`,
                     animation: `pulse 1s ease-in-out infinite alternate`,
                     animationDelay: `${Math.random()}s`
                  }}
               ></div>
            ))}
         </div>

         {/* Ergosphere (Spinning region) */}
         <div className={`absolute w-32 h-16 rounded-full border border-orange-500/30 bg-orange-900/20 animate-[spin_1s_linear_infinite] ${critical && 'bg-red-900/40 border-red-500/50'}`}></div>

         {/* Event Horizon (Pure Black) */}
         <div className="relative z-10 w-8 h-8 rounded-full bg-black shadow-[0_0_20px_#f97316] flex items-center justify-center" style={{ boxShadow: critical ? '0 0 40px #ef4444' : '0 0 20px #f97316' }}>
            {/* Accretion ring inside */}
            <div className="absolute w-12 h-12 rounded-full border-t-2 border-b-2 border-white/80 rotate-45 animate-[spin_0.5s_linear_infinite]"></div>
         </div>
         
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Horizon Temp</div>
            <div className={`text-lg font-mono font-bold ${critical ? 'text-red-400' : 'text-orange-400'}`}>
               {temperature.toExponential(2)} <span className="text-xs">K</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Power Output</div>
            <div className="text-lg font-mono font-bold text-sky-400">
               {powerOutput.toExponential(2)} <span className="text-xs">W</span>
            </div>
         </div>
      </div>

      <div className="space-y-2 mb-2">
         <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400">Singularity Mass</span>
            <span className="font-bold font-mono text-white">{(bhMass / 1e3).toFixed(1)} Tons</span>
         </div>
         {/* Mass Bar (Depleting) */}
         <div className="w-full h-1 bg-red-900/30 rounded relative">
            <div className="absolute top-0 bottom-0 left-0 bg-white transition-all" style={{ width: `${Math.min(100, (bhMass / 2e8) * 100)}%` }}></div>
         </div>
      </div>
    </div>
  );
};
