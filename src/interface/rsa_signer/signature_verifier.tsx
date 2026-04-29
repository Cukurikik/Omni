import React, { useState, useEffect } from 'react';

export const SignatureVerifier: React.FC = () => {
  const [verifications, setVerifications] = useState<{hash: string, valid: boolean}[]>([]);

  useEffect(() => {
    let count = 0;
    const interval = setInterval(() => {
      count++;
      
      const hash = `0x${Math.floor(Math.random()*16777215).toString(16).padStart(6, '0').toUpperCase()}...`;
      const valid = Math.random() > 0.1; // 90% valid signatures
      
      setVerifications(prev => {
        const next = [{ hash, valid }, ...prev];
        return next.slice(0, 5);
      });

    }, 600);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 flex justify-between items-center border-b border-slate-700 pb-3">
        <div>
          <h2 className="text-xl font-bold text-fuchsia-400">RSA-PSS Signer</h2>
          <p className="text-xs text-slate-400">Digital Signature Verification</p>
        </div>
        <div className="text-[10px] font-mono bg-slate-800 text-slate-400 px-2 py-1 rounded">
          2048-BIT
        </div>
      </div>

      <div className="flex flex-col gap-3">
        {verifications.map((v, i) => (
          <div key={i} className="flex justify-between items-center bg-slate-800 p-3 rounded border border-slate-700 shadow-sm">
             <div className="flex items-center gap-3">
                <div className="text-slate-500">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
                  </svg>
                </div>
                <div className="font-mono text-sm text-slate-300">{v.hash}</div>
             </div>
             
             <div className={`text-[10px] font-bold px-2 py-1 rounded
               ${v.valid ? 'bg-emerald-900/50 text-emerald-400' : 'bg-rose-900/50 text-rose-400'}
             `}>
               {v.valid ? 'VERIFIED' : 'INVALID'}
             </div>
          </div>
        ))}
      </div>
    </div>
  );
};
