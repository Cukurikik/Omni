import React, { useState, useEffect } from 'react';

export const SpacetimeRipple: React.FC = () => {
  const [strain, setStrain] = useState(0);
  const [chirpFreq, setChirpFreq] = useState(0);
  const [mergerActive, setMergerActive] = useState(false);

  useEffect(() => {
    let t = 0;
    let wave: NodeJS.Timeout;

    if (mergerActive) {
       // Simulate the "Chirp" waveform (frequency and amplitude increase until merger)
       wave = setInterval(() => {
          t += 0.05;
          
          // Inspiral phase
          if (t < 4.0) {
             const freq = 10 + (t * 20); // Frequency increases
             const amp = 0.5 + (t * 0.2); // Amplitude increases
             setChirpFreq(freq);
             setStrain(Math.sin(t * freq) * amp);
          } 
          // Merger (Ringdown)
          else if (t >= 4.0 && t < 5.0) {
             const decay = Math.exp(-(t - 4.0) * 5);
             setStrain(Math.sin(t * 150) * 2.0 * decay);
          } 
          // Reset
          else {
             setMergerActive(false);
             setStrain(0);
             setChirpFreq(0);
             t = 0;
          }
       }, 50);
    } else {
       // Background quantum/seismic noise
       wave = setInterval(() => {
          setStrain((Math.random() - 0.5) * 0.1);
       }, 50);
    }

    return () => clearInterval(wave);
  }, [mergerActive]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-blue-400">Gravitational Wave</h2>
          <p className="text-xs text-slate-400">LIGO Interferometer</p>
        </div>
        <button 
           onClick={() => !mergerActive && setMergerActive(true)}
           className={`px-3 py-1 font-bold text-[10px] rounded border transition-colors ${mergerActive ? 'bg-blue-900/50 text-blue-400 border-blue-800' : 'bg-slate-800 text-slate-400 border-slate-600 hover:bg-slate-700'}`}
           disabled={mergerActive}
        >
           {mergerActive ? 'CHIRP DETECTED' : 'SIMULATE MERGER'}
        </button>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex flex-col items-center justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* Spacetime Grid (Distorted by the wave) */}
         <div className="absolute inset-0 flex items-center justify-center opacity-40">
            {/* Horizontal lines squeezing/stretching */}
            <div className="absolute inset-0 flex flex-col justify-around transition-all duration-75" style={{ transform: `scaleY(${1 + strain * 0.2})` }}>
               {[...Array(10)].map((_, i) => <div key={`h-${i}`} className="w-full h-px bg-blue-500/50"></div>)}
            </div>
            {/* Vertical lines squeezing/stretching (opposite phase) */}
            <div className="absolute inset-0 flex justify-around transition-all duration-75" style={{ transform: `scaleX(${1 - strain * 0.2})` }}>
               {[...Array(15)].map((_, i) => <div key={`v-${i}`} className="h-full w-px bg-blue-500/50"></div>)}
            </div>
         </div>

         {/* Black Hole Merger Visual (Center) */}
         {mergerActive && (
            <div className="relative z-10 w-24 h-24 flex items-center justify-center transition-all duration-75" style={{ transform: `rotate(${chirpFreq * 10}deg) scale(${1 - chirpFreq/200})` }}>
               {/* Two black holes spiraling in */}
               <div className="absolute left-0 w-4 h-4 bg-black rounded-full shadow-[0_0_15px_#fff] border border-slate-700"></div>
               <div className="absolute right-0 w-4 h-4 bg-black rounded-full shadow-[0_0_15px_#fff] border border-slate-700"></div>
               {/* Gravity wave ripples radiating outwards */}
               <div className="absolute w-32 h-32 border border-blue-500/30 rounded-[50%] animate-ping" style={{ animationDuration: '0.5s' }}></div>
            </div>
         )}

         {/* Oscilloscope Waveform overlay */}
         <div className="absolute bottom-4 left-4 right-4 h-16 border border-slate-700 bg-black/50 rounded flex items-end">
            <div 
               className="w-2 h-full bg-emerald-400 shadow-[0_0_10px_#34d399] transition-all duration-75"
               style={{ height: `${50 + (strain * 20)}%` }}
            ></div>
            <div className="ml-2 text-[10px] font-mono text-emerald-400">h(t)</div>
         </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Strain (h)</div>
            <div className="text-lg font-mono font-bold text-emerald-400">
               {strain === 0 ? '0.00' : (strain * 1e-21).toExponential(2)}
            </div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Chirp Freq</div>
            <div className="text-lg font-mono font-bold text-sky-400">
               {chirpFreq.toFixed(0)} <span className="text-xs">Hz</span>
            </div>
         </div>
      </div>

      <div className="grid grid-cols-1 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded text-center">
         <span>Classification: <span className="text-white">{chirpFreq > 0 ? 'BINARY BLACK HOLE MERGER' : 'NOISE FLOOR'}</span></span>
      </div>
    </div>
  );
};
