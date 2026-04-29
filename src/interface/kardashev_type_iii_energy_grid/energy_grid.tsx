import React, { useState, useEffect } from 'react';

export const EnergyGrid: React.FC = () => {
  const [accretionRate, setAccretionRate] = useState(1.0); // Solar masses per year
  const [powerOutput, setPowerOutput] = useState(100000); // Yottawatts
  const [gridDemand, setGridDemand] = useState(150000); // Yottawatts
  const [blackHoleSpin, setBlackHoleSpin] = useState(0.998); // Maximally spinning Kerr BH
  const [brownout, setBrownout] = useState(true);

  useEffect(() => {
    // Simulate Galactic Power Grid
    const grid = setInterval(() => {
       // Random fluctuations in demand
       setGridDemand(prev => prev + (Math.random() - 0.5) * 5000);
       
       // Calculate power based on accretion rate and spin efficiency (up to ~42%)
       const efficiency = 0.057 + (0.365 * Math.pow(blackHoleSpin, 3));
       // Simplified scaling: 1 solar mass/yr * 42% efficiency = ~1.2e39 watts = ~1.2e15 YW
       // Scaled down massively for UI readability
       const newPower = accretionRate * efficiency * 1000000;
       
       setPowerOutput(newPower);
       setBrownout(newPower < gridDemand);
       
    }, 500);

    return () => clearInterval(grid);
  }, [accretionRate, blackHoleSpin, gridDemand]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-yellow-400">Type III Grid</h2>
          <p className="text-xs text-slate-400">SMBH Quasar Extraction</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-bold border ${brownout ? 'bg-orange-900/50 text-orange-400 border-orange-800 animate-pulse' : 'bg-slate-800 text-emerald-400 border-slate-700'}`}>
          {brownout ? 'GALACTIC BROWNOUT' : 'GRID SATISFIED'}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex flex-col items-center justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)] perspective-[600px]">
         
         {/* Galactic Starfield */}
         <div className="absolute inset-0 flex items-center justify-center opacity-30">
            {[...Array(50)].map((_, i) => (
               <div key={i} className={`absolute w-px h-px rounded-full ${brownout ? 'bg-orange-500' : 'bg-emerald-400'}`} style={{
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                  opacity: Math.random(),
                  boxShadow: `0 0 5px ${brownout ? '#f97316' : '#34d399'}`
               }}></div>
            ))}
         </div>

         {/* Supermassive Black Hole */}
         <div className="relative z-20 w-16 h-16 rounded-full bg-black shadow-[0_0_20px_#000] border border-slate-800 flex items-center justify-center">
            {/* Event Horizon glow */}
            <div className="absolute inset-0 rounded-full shadow-[inset_0_0_10px_rgba(255,255,255,0.2)]"></div>
         </div>

         {/* Accretion Disk */}
         <div 
            className="absolute z-10 w-48 h-48 border-[16px] border-yellow-500/80 rounded-full flex items-center justify-center"
            style={{ 
               transform: 'rotateX(75deg)', 
               boxShadow: '0 0 50px #eab308, inset 0 0 30px #ca8a04',
               animation: `spin ${2 - accretionRate}s linear infinite`
            }}
         >
            {/* Plasma swirling in */}
            <div className="w-full h-full rounded-full border-t-[8px] border-white/50 blur-sm"></div>
         </div>

         {/* Polar Relativistic Jets (Quasar beams) */}
         <div className="absolute z-0 w-4 h-[120%] bg-gradient-to-t from-transparent via-cyan-400 to-transparent blur-md mix-blend-screen opacity-80" style={{ boxShadow: '0 0 30px #22d3ee' }}></div>
         <div className="absolute z-30 w-1 h-[120%] bg-white blur-[1px] opacity-90"></div>

      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Grid Demand</div>
            <div className="text-lg font-mono font-bold text-slate-300">
               {(gridDemand/1000).toFixed(1)}k <span className="text-xs text-slate-500">YW</span>
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Quasar Output</div>
            <div className={`text-lg font-mono font-bold ${brownout ? 'text-orange-400' : 'text-emerald-400'}`}>
               {(powerOutput/1000).toFixed(1)}k <span className="text-xs text-slate-500">YW</span>
            </div>
         </div>
      </div>

      <div className="w-full bg-slate-950 rounded border border-slate-800 p-2 flex flex-col gap-2">
         <div className="flex justify-between items-center">
            <span className="text-[10px] font-mono text-slate-500">Accretion Rate (M☉/yr)</span>
            <input 
               type="range" min="0.1" max="5.0" step="0.1" value={accretionRate} 
               onChange={(e) => setAccretionRate(parseFloat(e.target.value))}
               className="w-1/2 accent-yellow-500"
            />
         </div>
      </div>

      <style>{`
        @keyframes spin { 100% { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
};
