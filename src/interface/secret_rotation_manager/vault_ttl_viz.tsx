import React, { useState, useEffect } from 'react';

export const VaultTtlViz: React.FC = () => {
  const [ttl, setTtl] = useState(30); // 30 days
  const [rotating, setRotating] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setTtl(prev => {
         if (prev <= 0 && !rotating) {
            setRotating(true);
            setTimeout(() => {
               setTtl(30);
               setRotating(false);
            }, 2000);
            return 0;
         }
         return rotating ? 0 : prev - 1; // Simulate days passing quickly
      });
    }, 400); // 400ms = 1 day
    return () => clearInterval(interval);
  }, [rotating]);

  const entropyPercent = Math.max(0, (ttl / 30) * 100);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-fuchsia-500">Zero-Trust Vault</h2>
          <p className="text-xs text-slate-400">Dynamic Secret Rotation</p>
        </div>
        <div className="px-2 py-1 bg-slate-800 text-fuchsia-400 text-[10px] font-mono rounded border border-fuchsia-900/50">
          SOC2 Compliant
        </div>
      </div>

      <div className="bg-slate-950 p-6 rounded border border-slate-800 flex flex-col items-center justify-center mb-4">
         {rotating ? (
            <div className="flex flex-col items-center animate-fade-in py-4">
               <div className="w-8 h-8 border-4 border-fuchsia-500 border-t-transparent rounded-full animate-spin mb-3"></div>
               <div className="text-xs text-fuchsia-400 font-mono">Generating PKCS#11 HSM Key...</div>
            </div>
         ) : (
            <>
               <div className="text-[10px] uppercase font-bold text-slate-500 mb-2">Credential TTL</div>
               <div className={`text-5xl font-mono font-bold drop-shadow-md transition-colors
                  ${ttl > 15 ? 'text-emerald-400' : ttl > 5 ? 'text-amber-400' : 'text-red-500'}
               `}>
                  {ttl} <span className="text-lg">days</span>
               </div>
               
               <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden mt-4 border border-slate-700">
                  <div 
                    className={`h-full transition-all duration-300 ${ttl > 15 ? 'bg-emerald-500' : ttl > 5 ? 'bg-amber-500' : 'bg-red-500'}`}
                    style={{ width: `${entropyPercent}%` }}
                  ></div>
               </div>
               <div className="text-[8px] font-mono text-slate-500 mt-1">Entropy Decay Curve</div>
            </>
         )}
      </div>
      
      <div className="flex justify-between text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Target: DB_PROD_01</span>
         <span>Method: <span className="text-emerald-400">Hot-Swap</span></span>
      </div>
    </div>
  );
};
