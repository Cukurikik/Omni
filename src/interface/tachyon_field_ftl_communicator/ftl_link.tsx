import React, { useState, useEffect } from 'react';

export const FtlLink: React.FC = () => {
  const [latencyMs, setLatencyMs] = useState(0);
  const [messages, setMessages] = useState<{id: number, text: string, time: string, isParadox: boolean}[]>([]);
  const [counter, setCounter] = useState(0);

  useEffect(() => {
    // FTL communication allows negative latency (receiving before sending in certain frames)
    const comms = setInterval(() => {
       setLatencyMs(prev => {
          const noise = (Math.random() - 0.5) * 10;
          return -45 + noise; // Negative 45 milliseconds!
       });
       
       setCounter(c => {
          if (c % 5 === 0) {
             const isParadox = Math.random() > 0.8;
             const newMsg = {
                id: c,
                text: isParadox ? "ABORT: PREVENT EVENT X" : "Alpha Centauri telemetry OK",
                time: `T${isParadox ? '-' : '+'}0.0${Math.floor(Math.random()*99)}s`,
                isParadox
             };
             setMessages(prev => [newMsg, ...prev].slice(0, 5));
          }
          return c + 1;
       });
    }, 500);

    return () => clearInterval(comms);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-violet-400">Tachyon Comm-Link</h2>
          <p className="text-xs text-slate-400">Superluminal Array</p>
        </div>
        <div className="px-2 py-1 rounded text-[10px] font-mono border bg-violet-900/30 text-violet-400 border-violet-800 animate-pulse">
          FTL LINK ACTIVE
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[160px] flex flex-col justify-end relative overflow-hidden">
         
         {/* Space/Time grid distortion */}
         <div className="absolute inset-0 opacity-20">
            <svg className="w-full h-full">
               <defs>
                  <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                     <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#8b5cf6" strokeWidth="1"/>
                  </pattern>
               </defs>
               <rect width="100%" height="100%" fill="url(#grid)" className="animate-[pulse_2s_ease-in-out_infinite]" style={{ transformOrigin: 'center', transform: 'scale(1.5) perspective(100px) rotateX(20deg)' }} />
            </svg>
         </div>

         {/* Particle Stream */}
         <div className="absolute inset-x-0 top-1/2 h-4 flex items-center justify-center">
            <div className="w-full h-px bg-violet-500/50 shadow-[0_0_10px_#8b5cf6]"></div>
            {[...Array(5)].map((_, i) => (
               <div key={i} className="w-4 h-1 bg-white absolute rounded-full shadow-[0_0_8px_#fff]" style={{ animation: `slide-right ${0.5 + Math.random()}s linear infinite`, left: '-10%' }}></div>
            ))}
         </div>
      </div>
      
      <div className="bg-slate-950 p-2 rounded border border-slate-800 mb-4 h-24 overflow-hidden font-mono text-[10px]">
         <div className="text-slate-500 mb-1 border-b border-slate-800 pb-1">INCOMING TACHYON STREAM:</div>
         {messages.map(m => (
            <div key={m.id} className={`flex justify-between ${m.isParadox ? 'text-red-400 line-through opacity-50' : 'text-violet-300'}`}>
               <span>[{m.time}]</span>
               <span className="truncate ml-2 text-right">{m.isParadox ? 'CENSORED BY NOVIKOV LOOP' : m.text}</span>
            </div>
         ))}
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4 text-center">
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Causality Delta</div>
            <div className="text-lg font-mono font-bold text-sky-400">{latencyMs.toFixed(1)} <span className="text-xs">ms</span></div>
         </div>
         <div className="bg-slate-950 p-2 rounded border border-slate-800">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Target Distance</div>
            <div className="text-lg font-mono font-bold text-white">4.37 <span className="text-xs">LY</span></div>
         </div>
      </div>

      <div className="grid grid-cols-1 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded text-center">
         <span>Exotic Matter Throat: <span className="text-emerald-400">Stable -5.5e15 J</span></span>
      </div>

      <style>{`
        @keyframes slide-right {
          from { transform: translateX(0); }
          to { transform: translateX(400px); }
        }
      `}</style>
    </div>
  );
};
