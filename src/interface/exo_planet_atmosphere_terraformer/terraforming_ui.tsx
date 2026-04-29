import React, { useState, useEffect } from 'react';

export const TerraformingUi: React.FC = () => {
  const [temperature, setTemperature] = useState(210); // Start freezing (Mars-like)
  const [pressure, setPressure] = useState(0.01); // 1% Earth pressure
  const [oxygen, setOxygen] = useState(0.1);
  const [year, setYear] = useState(2150);

  useEffect(() => {
    // Simulate Terraforming Process (takes hundreds of years)
    const terraform = setInterval(() => {
       setYear(prev => prev + 1);
       
       // Warm up the planet via artificial greenhouse gases
       setTemperature(prev => Math.min(288, prev + 0.5)); // Target 288K (15C)
       
       // Increase pressure via crashing comets and sublimating dry ice
       setPressure(prev => Math.min(1.0, prev + 0.005));
       
       // Cyanobacteria converting CO2 to O2
       if (temperature > 273 && pressure > 0.1) {
          setOxygen(prev => Math.min(21.0, prev + 0.15));
       }
    }, 100);

    return () => clearInterval(terraform);
  }, [temperature, pressure]);

  const isHabitable = temperature > 273 && pressure > 0.06 && oxygen > 15.0;

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-green-400">Terraforming</h2>
          <p className="text-xs text-slate-400">Atmospheric Engineering</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-bold border ${isHabitable ? 'bg-green-900/50 text-green-400 border-green-800 shadow-[0_0_10px_#22c55e]' : 'bg-slate-800 text-slate-400 border-slate-700'}`}>
          {isHabitable ? 'BIOSPHERE ACTIVE' : 'SEEDING PHASE'}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex items-center justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* Space Background */}
         <div className="absolute inset-0 bg-black"></div>

         {/* The Planet */}
         <div className="relative w-40 h-40 rounded-full shadow-[inset_-20px_-20px_40px_rgba(0,0,0,0.9)] overflow-hidden" 
              style={{ 
                 // Planet color changes from red/brown to blue/green
                 background: temperature < 260 ? '#8c3a1e' : (temperature < 273 ? '#7a5a3a' : '#1e40af'),
                 transition: 'background 1s ease-in-out'
              }}>
            
            {/* Terrain / Continents */}
            <div className={`absolute inset-0 opacity-60 mix-blend-overlay transition-opacity duration-1000 ${temperature < 273 ? 'opacity-30' : 'opacity-100'}`} style={{
               background: 'radial-gradient(circle at 30% 40%, #22c55e 0%, transparent 40%), radial-gradient(circle at 70% 60%, #16a34a 0%, transparent 50%)'
            }}></div>

            {/* Ice Caps (melt as temperature rises) */}
            <div className="absolute top-0 left-0 right-0 h-12 bg-white blur-[2px] transition-all duration-1000" style={{ transform: `scaleY(${Math.max(0, (273 - temperature) / 60)})`, transformOrigin: 'top' }}></div>
            <div className="absolute bottom-0 left-0 right-0 h-12 bg-white blur-[2px] transition-all duration-1000" style={{ transform: `scaleY(${Math.max(0, (273 - temperature) / 60)})`, transformOrigin: 'bottom' }}></div>

            {/* Atmosphere layer (Thickens as pressure rises) */}
            <div className="absolute inset-0 rounded-full shadow-[inset_0_0_20px_#60a5fa] transition-opacity duration-1000" style={{ opacity: pressure }}></div>
         </div>
         
         {/* Atmospheric glow extending into space */}
         <div className="absolute w-44 h-44 rounded-full bg-blue-400/20 blur-xl transition-opacity duration-1000 pointer-events-none" style={{ opacity: pressure }}></div>

      </div>
      
      <div className="grid grid-cols-3 gap-2 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800 flex flex-col items-center">
            <div className="text-[9px] uppercase text-slate-500 mb-1">Temp</div>
            <div className={`text-base font-mono font-bold ${temperature > 273 ? 'text-green-400' : 'text-sky-400'}`}>
               {temperature.toFixed(1)}<span className="text-[10px]">K</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800 flex flex-col items-center">
            <div className="text-[9px] uppercase text-slate-500 mb-1">Pressure</div>
            <div className={`text-base font-mono font-bold ${pressure > 0.5 ? 'text-green-400' : 'text-amber-400'}`}>
               {pressure.toFixed(2)}<span className="text-[10px]">atm</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800 flex flex-col items-center">
            <div className="text-[9px] uppercase text-slate-500 mb-1">Oxygen</div>
            <div className={`text-base font-mono font-bold ${oxygen > 15 ? 'text-green-400' : 'text-slate-400'}`}>
               {oxygen.toFixed(1)}<span className="text-[10px]">%</span>
            </div>
         </div>
      </div>

      <div className="w-full bg-slate-950 rounded border border-slate-800 p-2 flex justify-between items-center px-4">
         <span className="text-xs text-slate-400 font-mono">Current Year:</span>
         <span className="text-lg text-white font-mono font-bold">{year} AD</span>
      </div>
    </div>
  );
};
