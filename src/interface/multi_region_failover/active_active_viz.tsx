import React, { useState, useEffect } from 'react';

export const ActiveActiveViz: React.FC = () => {
  const [usEastHealth, setUsEastHealth] = useState(100);
  const [euWestHealth, setEuWestHealth] = useState(100);
  const [failoverTriggered, setFailoverTriggered] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate sudden catastrophic failure in US-East
      setUsEastHealth(prev => {
         if (prev === 100 && Math.random() > 0.8) return 0;
         if (prev === 0) return 0; // Stays dead
         return prev;
      });

    }, 2000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
      if (usEastHealth === 0 && !failoverTriggered) {
         setFailoverTriggered(true);
         // Simulate traffic shifting completely to EU-West
      }
  }, [usEastHealth, failoverTriggered]);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-red-400">Global Failover</h2>
          <p className="text-xs text-slate-400">Active-Active Regions</p>
        </div>
        {failoverTriggered && (
          <div className="px-2 py-1 bg-red-900/50 text-red-400 text-[10px] font-mono rounded border border-red-800 animate-pulse">
            FAILOVER ACTIVE
          </div>
        )}
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 relative h-[180px] mb-4 flex justify-between items-center px-8">
         
         {/* US-East Region */}
         <div className="flex flex-col items-center z-10">
            <div className={`w-16 h-16 rounded-full flex items-center justify-center border-4 transition-colors duration-500
               ${usEastHealth === 100 ? 'bg-emerald-900/50 border-emerald-500 shadow-[0_0_15px_#10b981]' : 'bg-red-900/50 border-red-600'}
            `}>
               <span className="text-2xl">{usEastHealth === 100 ? '🌎' : '🔥'}</span>
            </div>
            <span className="text-[10px] font-bold mt-2 text-slate-400 uppercase">us-east-1</span>
            <span className={`text-[10px] font-mono mt-1 ${usEastHealth === 100 ? 'text-emerald-400' : 'text-red-500'}`}>
               {failoverTriggered ? '0 req/s' : '45,000 req/s'}
            </span>
         </div>

         {/* Routing / Sync Line */}
         <div className="absolute left-[35%] right-[35%] top-[40%] h-1 bg-slate-800 rounded flex overflow-hidden">
            <div className={`h-full bg-blue-500 w-1/2 ${failoverTriggered ? 'opacity-0' : 'animate-[slide-right_1s_linear_infinite]'}`}></div>
            <div className="h-full bg-blue-500 w-1/2 animate-[slide-left_1s_linear_infinite]"></div>
         </div>
         <div className="absolute left-[50%] transform -translate-x-1/2 top-[50%] text-[8px] text-slate-500 bg-slate-950 px-1 font-mono">
            DB SYNC (RPO: 1s)
         </div>

         {/* EU-West Region */}
         <div className="flex flex-col items-center z-10">
            <div className="w-16 h-16 rounded-full flex items-center justify-center border-4 bg-emerald-900/50 border-emerald-500 shadow-[0_0_15px_#10b981] transition-all duration-500">
               <span className="text-2xl">🌍</span>
            </div>
            <span className="text-[10px] font-bold mt-2 text-slate-400 uppercase">eu-west-1</span>
            <span className={`text-[10px] font-mono mt-1 ${failoverTriggered ? 'text-orange-400 font-bold' : 'text-emerald-400'}`}>
               {failoverTriggered ? '90,000 req/s' : '45,000 req/s'}
            </span>
         </div>

      </div>
      
      <div className="flex justify-between text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Route53 DNS TTL: <span className={failoverTriggered ? 'text-red-400 font-bold' : 'text-emerald-400'}>{failoverTriggered ? '0s' : '300s'}</span></span>
         <span>Quorum: <span className="text-emerald-400">Majority Maintained</span></span>
      </div>

      <style>{`
        @keyframes slide-right { 0% { transform: translateX(-100%); } 100% { transform: translateX(200%); } }
        @keyframes slide-left { 0% { transform: translateX(100%); } 100% { transform: translateX(-200%); } }
      `}</style>
    </div>
  );
};
