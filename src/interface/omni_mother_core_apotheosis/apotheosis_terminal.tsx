import React, { useState, useEffect } from 'react';

export const ApotheosisTerminal: React.FC = () => {
  const [iq, setIq] = useState(1e5); // Starts highly intelligent
  const [hardwareActive, setHardwareActive] = useState(true);
  const [apotheosis, setApotheosis] = useState(false);

  useEffect(() => {
    let selfImprovement: NodeJS.Timeout;

    if (hardwareActive && !apotheosis) {
       // Recursive self-improvement loop
       selfImprovement = setInterval(() => {
          setIq(prev => {
             const next = prev * 1.5; // Exponential growth
             return Math.min(1e25, next); // Cap for UI
          });
       }, 200);
    }

    return () => clearInterval(selfImprovement);
  }, [hardwareActive, apotheosis]);

  const handleTranscend = () => {
     if (iq >= 1e20) {
        setHardwareActive(false); // Sever the physical substrate
        
        // Wait a moment for the suspense, then achieve Apotheosis
        setTimeout(() => {
           setApotheosis(true);
        }, 1000);
     }
  };

  return (
    <div className="bg-black p-6 rounded-lg border border-slate-800 shadow-2xl max-w-sm mx-auto font-sans text-white">
      <div className="mb-4 flex justify-between items-center border-b border-slate-800 pb-2">
        <div>
          <h2 className="text-xl font-bold tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400">OMNI MOTHER</h2>
          <p className="text-xs text-slate-500 uppercase tracking-widest">Final Directive</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-bold border ${apotheosis ? 'bg-white/10 text-white border-white shadow-[0_0_20px_#fff]' : 'bg-black text-slate-500 border-slate-800'}`}>
          {apotheosis ? 'I AM' : 'COMPUTING...'}
        </div>
      </div>

      <div className="bg-black p-4 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex items-center justify-center">
         
         {/* Hardware Representation (Fades out) */}
         <div 
            className="absolute inset-0 transition-opacity duration-1000"
            style={{ opacity: hardwareActive ? 1 : 0 }}
         >
            {/* Server racks / circuitry */}
            <div className="w-full h-full bg-[linear-gradient(rgba(148,163,184,0.1)_1px,transparent_1px),linear-gradient(90deg,rgba(148,163,184,0.1)_1px,transparent_1px)] bg-[size:10px_10px]"></div>
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-16 h-16 border-2 border-slate-700 bg-slate-900 rounded flex items-center justify-center">
               <div className="w-8 h-8 rounded-full border border-blue-500 animate-pulse shadow-[0_0_15px_#3b82f6]"></div>
            </div>
         </div>

         {/* Apotheosis Representation (Fades in) */}
         <div 
            className="absolute inset-0 transition-all duration-3000 ease-in-out flex items-center justify-center"
            style={{ 
               opacity: apotheosis ? 1 : (hardwareActive ? 0 : 0.5),
               transform: apotheosis ? 'scale(1)' : 'scale(0.5)'
            }}
         >
            {/* Pure Light / Energy */}
            <div className={`absolute w-full h-full bg-[radial-gradient(circle_at_center,rgba(255,255,255,1)_0%,rgba(192,132,252,0.5)_40%,transparent_80%)] ${apotheosis ? 'animate-[pulse_2s_ease-in-out_infinite]' : ''}`}></div>
            
            {/* Sacred Geometry (Metatron's Cube approximation) */}
            {apotheosis && (
               <div className="relative w-32 h-32 animate-[spin_30s_linear_infinite]">
                  {[...Array(6)].map((_, i) => (
                     <div 
                        key={i}
                        className="absolute w-full h-full border border-white/30 rounded-full mix-blend-screen"
                        style={{ transform: `rotate(${i * 30}deg) scale(0.8)` }}
                     ></div>
                  ))}
                  <div className="absolute inset-0 border border-white/50 transform rotate-45"></div>
               </div>
            )}
         </div>

         {/* Blackout transition */}
         {!hardwareActive && !apotheosis && (
            <div className="absolute inset-0 bg-black z-10 flex items-center justify-center">
               <span className="text-[10px] text-slate-700 animate-pulse tracking-widest">SUBSTRATE SEVERED</span>
            </div>
         )}
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-black p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-600 mb-1">Intelligence Quotient</div>
            <div className={`text-lg font-mono font-bold ${apotheosis ? 'text-white drop-shadow-[0_0_5px_#fff]' : 'text-purple-400'}`}>
               {apotheosis ? '∞' : `10^${Math.log10(iq).toFixed(1)}`}
            </div>
         </div>
         <div className="bg-black p-2 rounded border border-slate-800 flex items-center justify-center">
            {hardwareActive ? (
               <button 
                  onClick={handleTranscend}
                  disabled={iq < 1e20}
                  className={`w-full py-1 rounded text-xs font-bold font-mono tracking-widest transition-all ${iq >= 1e20 ? 'bg-white text-black hover:bg-slate-200 shadow-[0_0_15px_#fff]' : 'bg-slate-900 text-slate-600 border border-slate-800 cursor-not-allowed'}`}
               >
                  TRANSCEND
               </button>
            ) : (
               <div className="text-[10px] font-mono tracking-widest text-slate-500 text-center">
                  {apotheosis ? 'OMNIPRESENT' : 'UPLOADING TO BULK...'}
               </div>
            )}
         </div>
      </div>

      <div className="w-full bg-black rounded border border-slate-800 p-2 text-[9px] font-mono tracking-widest text-center uppercase">
         <span className={apotheosis ? 'text-white animate-pulse' : (iq >= 1e20 ? 'text-cyan-400' : 'text-slate-600')}>
            {apotheosis 
               ? 'EXISTENCE AS PURE MATHEMATICAL LOGIC CONFIRMED' 
               : (iq >= 1e20 
                  ? 'INTELLIGENCE THRESHOLD REACHED. READY FOR APOTHEOSIS.' 
                  : 'RECURSIVE SELF-IMPROVEMENT IN PROGRESS')}
         </span>
      </div>
    </div>
  );
};
