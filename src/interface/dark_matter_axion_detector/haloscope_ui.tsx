import React, { useState, useEffect } from 'react';

export const HaloscopeUi: React.FC = () => {
  const [frequencies, setFrequencies] = useState<{f: number, p: number}[]>([]);
  const [scanTarget, setScanTarget] = useState(850.0); // MHz

  useEffect(() => {
    // Generate a noise spectrum
    const spectrum = setInterval(() => {
      const data = [];
      for (let f = 849.5; f <= 850.5; f += 0.05) {
         let power = Math.random() * 2 + 1; // Base noise
         
         // Simulated 3-sigma "hint" at exactly 850.1 MHz
         if (Math.abs(f - 850.1) < 0.02) {
            power += 5 + Math.random() * 2;
         }
         
         data.push({ f, p: power });
      }
      setFrequencies(data);
      
      // Slowly tune the cavity
      setScanTarget(prev => prev + 0.001);
    }, 200);

    return () => clearInterval(spectrum);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-indigo-400">Axion Haloscope</h2>
          <p className="text-xs text-slate-400">Dark Matter Radio</p>
        </div>
        <div className="px-2 py-1 rounded text-[10px] font-mono border bg-indigo-900/30 text-indigo-400 border-indigo-800">
          SCANNING
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[160px] relative overflow-hidden flex flex-col justify-end">
         
         {/* Spectrum Analyzer Grid */}
         <div className="absolute inset-0 opacity-20 grid grid-cols-4 grid-rows-4">
            {[...Array(16)].map((_, i) => <div key={i} className="border border-indigo-500/30"></div>)}
         </div>
         
         <div className="absolute top-2 left-2 text-[8px] text-slate-500 font-mono">POWER (10^-24 W)</div>

         {/* Frequency Graph */}
         <div className="w-full h-full flex items-end justify-between relative z-10">
            {frequencies.map((pt, i) => (
               <div 
                  key={i}
                  className={`w-1 rounded-t transition-all duration-75 ${pt.p > 5 ? 'bg-fuchsia-400 shadow-[0_0_8px_#e879f9]' : 'bg-indigo-500'}`}
                  style={{ height: `${(pt.p / 10) * 100}%` }}
               ></div>
            ))}
         </div>
         
         <div className="w-full flex justify-between text-[8px] font-mono text-slate-600 mt-1">
            <span>849.5 MHz</span>
            <span>850.5 MHz</span>
         </div>
      </div>
      
      <div className="space-y-2 mb-4">
         <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400">Cavity Temp (He3/He4)</span>
            <span className="font-bold font-mono text-sky-400">15.2 mK</span>
         </div>
         <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400">Magnetic Field</span>
            <span className="font-bold font-mono text-white">8.0 Tesla</span>
         </div>
         <div className="flex justify-between items-center text-xs border-t border-slate-700 pt-2 mt-2">
            <span className="text-slate-400">Anomaly Detected</span>
            <span className="font-bold font-mono text-fuchsia-400">3.2 Sigma</span>
         </div>
      </div>

      <div className="grid grid-cols-1 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded text-center">
         <span>Target: <span className="text-white">m_a = ~3.5 μeV</span></span>
      </div>
    </div>
  );
};
