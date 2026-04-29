import React, { useState, useEffect } from 'react';

export const DriftDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<{feature: string, ksDist: number, pValue: number, isDrift: boolean}[]>([]);

  useEffect(() => {
    // Deterministic Drift metrics
    const initial = [
      { feature: 'transaction_amt', ksDist: 0.05, pValue: 0.45, isDrift: false },
      { feature: 'user_age', ksDist: 0.02, pValue: 0.89, isDrift: false },
      { feature: 'location_id', ksDist: 0.12, pValue: 0.01, isDrift: true } // Drifted
    ];
    setMetrics(initial);

    let t = 0;
    const interval = setInterval(() => {
      t++;
      setMetrics(prev => prev.map(m => {
        if (m.feature === 'transaction_amt') {
          // Simulate gradual drift over time
          const dist = 0.05 + (t * 0.005);
          const p = Math.max(0.001, 0.45 - (t * 0.02));
          return { ...m, ksDist: dist, pValue: p, isDrift: dist > 0.1 && p < 0.05 };
        }
        return m;
      }));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-xl border border-slate-700 shadow-2xl max-w-2xl mx-auto font-sans text-slate-100">
      <div className="mb-6 flex justify-between items-center border-b border-slate-700 pb-4">
        <div>
          <h2 className="text-xl font-bold text-red-500">Alibi Detect</h2>
          <p className="text-xs text-slate-400">KS-Test Drift Dashboard</p>
        </div>
        <div className="flex items-center gap-2">
           <div className={`w-3 h-3 rounded-full ${metrics.some(m => m.isDrift) ? 'bg-red-500 animate-pulse' : 'bg-emerald-500'}`}></div>
           <span className="text-xs font-bold font-mono">
             {metrics.some(m => m.isDrift) ? 'DRIFT DETECTED' : 'SYSTEM HEALTHY'}
           </span>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {metrics.map((m, i) => (
          <div key={i} className={`p-4 rounded border flex justify-between items-center transition-colors
            ${m.isDrift ? 'bg-red-950 border-red-900' : 'bg-slate-800 border-slate-700'}
          `}>
            <div className="flex-1">
              <h3 className="font-bold text-slate-200">{m.feature}</h3>
              <div className="text-xs text-slate-400 font-mono flex gap-4 mt-1">
                <span>KS-Dist: {m.ksDist.toFixed(4)}</span>
                <span>P-Val: {m.pValue.toFixed(4)}</span>
              </div>
            </div>
            
            <div className="w-32 bg-slate-950 h-2 rounded overflow-hidden mr-4 border border-slate-700">
               <div className={`h-full ${m.isDrift ? 'bg-red-500' : 'bg-emerald-500'}`} style={{width: `${Math.min(100, m.ksDist * 500)}%`}}></div>
            </div>

            <div className={`px-2 py-1 text-[10px] font-bold rounded
              ${m.isDrift ? 'bg-red-900 text-red-200' : 'bg-slate-700 text-slate-400'}
            `}>
              {m.isDrift ? 'ALERT' : 'NORMAL'}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
