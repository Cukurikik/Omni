import React, { useState, useEffect } from 'react';

export const TokenInspector: React.FC = () => {
  const [tokens, setTokens] = useState<{id: string, valid: boolean, type: string}[]>([]);

  useEffect(() => {
    let count = 0;
    const interval = setInterval(() => {
      count++;
      
      // Deterministic token stream
      const isExpired = count % 5 === 0;
      const isTampered = count % 8 === 0;
      
      let type = 'OK';
      let valid = true;
      
      if (isTampered) { type = 'TAMPERED'; valid = false; }
      else if (isExpired) { type = 'EXPIRED'; valid = false; }

      setTokens(prev => {
        const next = [{ id: `jwt_${count.toString().padStart(4, '0')}`, valid, type }, ...prev];
        return next.slice(0, 6);
      });

    }, 600);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-50 p-6 rounded-lg border border-slate-200 shadow-xl max-w-sm mx-auto font-sans">
      <div className="mb-6 border-b border-slate-200 pb-2 flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-amber-600">JWT Crypto</h2>
          <p className="text-xs text-slate-500">Live Auth Token Verification</p>
        </div>
        <div className="text-[10px] font-mono bg-white px-2 py-1 border border-slate-200 rounded text-slate-500">
          HMAC-SHA256
        </div>
      </div>

      <div className="flex flex-col gap-2">
        {tokens.map(t => (
          <div key={t.id} className="bg-white p-3 rounded border border-slate-200 shadow-sm flex justify-between items-center transition-colors">
            <div className="flex items-center gap-3">
              <div className="text-slate-400">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4v-4l5.659-5.659A6 6 0 1115 7z"></path>
                </svg>
              </div>
              <div className="font-mono text-sm font-bold text-slate-700">{t.id}</div>
            </div>
            
            <div className={`text-[10px] font-bold px-2 py-1 rounded
              ${t.type === 'OK' ? 'bg-emerald-100 text-emerald-700' : 
                t.type === 'EXPIRED' ? 'bg-amber-100 text-amber-700' : 'bg-rose-100 text-rose-700'}
            `}>
              {t.type}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
