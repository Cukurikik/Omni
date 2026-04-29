import React, { useState, useEffect } from 'react';

export const LimitMonitor: React.FC = () => {
  const [tokens, setTokens] = useState(10);
  const capacity = 10;
  const [rejected, setRejected] = useState(false);

  useEffect(() => {
    // Refill tokens
    const refillInterval = setInterval(() => {
      setTokens(prev => Math.min(capacity, prev + 1));
    }, 1000); // 1 token per second

    // Consume tokens
    const consumeInterval = setInterval(() => {
      setTokens(prev => {
        if (prev >= 1) {
          setRejected(false);
          return prev - 1;
        } else {
          setRejected(true);
          return 0;
        }
      });
    }, 800); // Request every 800ms (Faster than refill -> Will eventually rate limit)

    return () => {
      clearInterval(refillInterval);
      clearInterval(consumeInterval);
    };
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans">
      <div className="mb-6 flex justify-between items-center border-b border-slate-700 pb-3">
        <div>
          <h2 className="text-xl font-bold text-orange-500">Rate Limiter</h2>
          <p className="text-xs text-slate-400">Token Bucket Algorithm</p>
        </div>
        <div className="text-[10px] font-bold px-2 py-1 bg-slate-800 text-slate-400 rounded">
          SLA: FREE
        </div>
      </div>

      <div className="flex flex-col items-center gap-6">
        
        {/* Status Indicator */}
        <div className={`text-xl font-black tracking-widest px-6 py-2 rounded-full border-2 transition-colors duration-300
          ${rejected ? 'bg-red-900/30 text-red-500 border-red-500' : 'bg-emerald-900/30 text-emerald-500 border-emerald-500'}
        `}>
          {rejected ? '429 TOO MANY REQ' : '200 OK'}
        </div>

        {/* Bucket Visualization */}
        <div className="w-48 h-32 border-4 border-slate-700 rounded-b-xl border-t-0 relative flex items-end p-1 overflow-hidden bg-slate-950 shadow-inner">
          <div 
             className="w-full bg-orange-500 rounded-b-lg transition-all duration-300 ease-in-out"
             style={{ height: `${(tokens / capacity) * 100}%` }}
          ></div>
          <div className="absolute inset-0 flex items-center justify-center font-mono text-2xl font-black text-white mix-blend-difference drop-shadow-md">
            {tokens} / {capacity}
          </div>
        </div>
        
        <div className="text-xs text-slate-500 font-mono">Refill: 1 token / sec</div>

      </div>
    </div>
  );
};
