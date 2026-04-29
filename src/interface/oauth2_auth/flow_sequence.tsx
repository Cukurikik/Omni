import React, { useState, useEffect } from 'react';

export const FlowSequence: React.FC = () => {
  const [flows, setFlows] = useState<{id: string, step: string, status: string}[]>([]);

  useEffect(() => {
    let count = 0;
    const interval = setInterval(() => {
      count++;
      
      const newFlow = {
        id: `OAUTH_${count.toString().padStart(4, '0')}`,
        step: 'Initiated',
        status: 'PENDING'
      };
      
      setFlows(prev => {
        const active = prev.map(f => {
          if (f.status === 'DONE') return f;
          
          if (f.step === 'Initiated') return { ...f, step: 'Authorize' };
          if (f.step === 'Authorize') return { ...f, step: 'Token Exchanged' };
          if (f.step === 'Token Exchanged') return { ...f, step: 'Verified', status: 'DONE' };
          
          return f;
        });
        
        return [newFlow, ...active].slice(0, 6);
      });
      
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-50 p-6 rounded-lg border border-slate-200 shadow-xl max-w-lg mx-auto font-sans">
      <div className="mb-6 border-b border-slate-200 pb-2 flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-blue-600">OAuth2.0 PKCE</h2>
          <p className="text-xs text-slate-500">Authorization Code Flow</p>
        </div>
      </div>

      <div className="flex flex-col gap-3">
        {flows.map(f => (
          <div key={f.id} className="bg-white p-3 rounded border border-slate-200 shadow-sm flex items-center justify-between">
            <div className="font-mono text-sm font-bold text-slate-600 w-24">{f.id}</div>
            
            <div className="flex-1 px-4 relative">
              <div className="h-1 bg-slate-100 rounded w-full overflow-hidden">
                <div className="h-full bg-blue-500 transition-all duration-300" style={{
                  width: f.step === 'Initiated' ? '25%' : 
                         f.step === 'Authorize' ? '50%' : 
                         f.step === 'Token Exchanged' ? '75%' : '100%'
                }}></div>
              </div>
              <div className="text-[10px] font-bold text-slate-400 mt-1 text-center w-full uppercase">
                {f.step}
              </div>
            </div>
            
            <div className="w-8 flex justify-end">
              {f.status === 'DONE' ? (
                <svg className="w-5 h-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                </svg>
              ) : (
                <div className="w-4 h-4 border-2 border-slate-300 border-t-blue-500 rounded-full animate-spin"></div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
