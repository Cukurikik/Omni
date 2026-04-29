import React, { useState, useEffect } from 'react';

export const BreakerDashboard: React.FC = () => {
  const [state, setState] = useState('CLOSED');
  const [errorRate, setErrorRate] = useState(0.0);

  useEffect(() => {
    let t = 0;
    const interval = setInterval(() => {
      t++;
      
      // Deterministic simulation of an outage and recovery
      if (t > 5 && t < 15) {
        // Spike errors
        setErrorRate(prev => Math.min(1.0, prev + 0.15));
      } else {
        // Recover
        setErrorRate(prev => Math.max(0.0, prev - 0.1));
      }

      setErrorRate(currentRate => {
        setState(currState => {
          if (currState === 'CLOSED' && currentRate >= 0.5) return 'OPEN';
          if (currState === 'OPEN' && currentRate < 0.5 && t > 12) return 'HALF_OPEN';
          if (currState === 'HALF_OPEN' && currentRate <= 0.1) return 'CLOSED';
          if (currState === 'HALF_OPEN' && currentRate > 0.1) return 'OPEN';
          return currState;
        });
        return currentRate;
      });

    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 flex justify-between items-center border-b border-slate-700 pb-3">
        <div>
          <h2 className="text-xl font-bold text-orange-500">Circuit Breaker</h2>
          <p className="text-xs text-slate-400">Systemic Flow Control</p>
        </div>
      </div>

      <div className="flex flex-col items-center gap-6">
        
        {/* Status Indicator */}
        <div className={`text-2xl font-black tracking-widest px-8 py-3 rounded-xl border-2 transition-colors duration-500 shadow-lg
          ${state === 'CLOSED' ? 'bg-emerald-900/30 text-emerald-500 border-emerald-500 shadow-emerald-900/50' : 
            state === 'OPEN' ? 'bg-red-900/30 text-red-500 border-red-500 shadow-red-900/50' : 
            'bg-amber-900/30 text-amber-500 border-amber-500 shadow-amber-900/50'}
        `}>
          {state}
        </div>

        <div className="w-full bg-slate-800 p-4 rounded border border-slate-700">
          <div className="flex justify-between text-xs font-bold text-slate-400 mb-2">
            <span>EMA Error Rate</span>
            <span>{(errorRate * 100).toFixed(1)}%</span>
          </div>
          
          <div className="h-2 bg-slate-700 rounded overflow-hidden relative">
            {/* Threshold marker */}
            <div className="absolute top-0 bottom-0 w-0.5 bg-slate-400 z-10" style={{left: '50%'}}></div>
            
            <div className={`h-full transition-all duration-300
              ${errorRate >= 0.5 ? 'bg-red-500' : 'bg-emerald-500'}
            `} style={{width: `${errorRate * 100}%`}}></div>
          </div>
          
          <div className="text-[10px] text-slate-500 text-center mt-3">
            {state === 'CLOSED' ? 'Traffic flowing normally. Monitoring errors.' :
             state === 'OPEN' ? 'Traffic blocked. Failing fast to prevent cascade.' :
             'Testing upstream recovery with limited traffic.'}
          </div>
        </div>

      </div>
    </div>
  );
};
