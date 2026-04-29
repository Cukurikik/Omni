import React, { useState, useEffect } from 'react';

export const HsmUi: React.FC = () => {
  const [state, setState] = useState<'IDLE' | 'AWAITING_DEVICE' | 'SIGNING' | 'SIGNED'>('IDLE');

  useEffect(() => {
    let timer1: NodeJS.Timeout, timer2: NodeJS.Timeout;
    
    // Auto-simulate the signing flow
    const flow = setInterval(() => {
       setState('AWAITING_DEVICE');
       
       timer1 = setTimeout(() => {
          setState('SIGNING');
          
          timer2 = setTimeout(() => {
             setState('SIGNED');
             setTimeout(() => setState('IDLE'), 2000);
          }, 1500); // Compute time on secure element
          
       }, 3000); // Wait for human to press buttons
       
    }, 8000);

    return () => { clearInterval(flow); clearTimeout(timer1); clearTimeout(timer2); };
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-zinc-300">Hardware Wallet</h2>
          <p className="text-xs text-slate-400">USB HID Secure Enclave</p>
        </div>
        <div className={`w-2 h-2 rounded-full ${state !== 'IDLE' ? 'bg-amber-500 animate-pulse shadow-[0_0_8px_#f59e0b]' : 'bg-slate-600'}`}></div>
      </div>

      <div className="bg-zinc-800 p-6 rounded border-2 border-zinc-700 mb-4 flex flex-col items-center justify-center relative shadow-inner">
         
         {/* Device Mockup */}
         <div className="w-32 h-12 bg-zinc-900 rounded-sm border border-zinc-950 flex flex-col items-center justify-center relative overflow-hidden">
            {/* Screen */}
            <div className="w-24 h-6 bg-cyan-950 border border-cyan-900 flex items-center justify-center">
               <span className="text-[8px] font-mono text-cyan-400">
                  {state === 'IDLE' && 'Ready.'}
                  {state === 'AWAITING_DEVICE' && 'Approve TX?'}
                  {state === 'SIGNING' && 'Signing...'}
                  {state === 'SIGNED' && 'Approved!'}
               </span>
            </div>
            
            {/* Physical Buttons (Simulating presses) */}
            <div className="absolute top-0 right-2 w-2 h-1 bg-zinc-700"></div>
            <div className="absolute top-0 left-2 w-2 h-1 bg-zinc-700"></div>
            
            {/* Simulated button press animation */}
            {state === 'AWAITING_DEVICE' && (
               <>
                 <div className="absolute top-0 right-2 w-2 h-1 bg-amber-500 animate-ping"></div>
                 <div className="absolute top-0 left-2 w-2 h-1 bg-amber-500 animate-ping"></div>
               </>
            )}
         </div>
      </div>
      
      <div className="space-y-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <div className="flex justify-between">
            <span>Status:</span>
            <span className={state === 'SIGNED' ? 'text-emerald-400 font-bold' : 'text-amber-400'}>{state}</span>
         </div>
         <div className="flex justify-between">
            <span>Curve:</span>
            <span className="text-white">secp256k1</span>
         </div>
         <div className="flex justify-between">
            <span>Payload:</span>
            <span className="text-slate-500 truncate ml-2">0x892a...f41</span>
         </div>
      </div>
    </div>
  );
};
