import React, { useState, useEffect } from 'react';

export const ActivityDashboard: React.FC = () => {
  const [aiTokens, setAiTokens] = useState(0);
  const [manualKeys, setManualKeys] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate developer typing vs AI autocomplete bursts
      if (Math.random() > 0.3) {
        setAiTokens(prev => prev + Math.floor(Math.random() * 40));
      } else {
        setManualKeys(prev => prev + Math.floor(Math.random() * 15));
      }
    }, 500);
    return () => clearInterval(interval);
  }, []);

  const total = aiTokens + manualKeys || 1;
  const aiRatio = (aiTokens / total) * 100;

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-fuchsia-400">IDE Telemetry</h2>
          <p className="text-xs text-slate-400">AI Productivity Metrics</p>
        </div>
        <div className="w-2 h-2 rounded-full bg-fuchsia-500 animate-pulse"></div>
      </div>

      <div className="flex gap-4 text-center mb-6">
         <div className="flex-1">
             <div className="text-2xl font-mono text-fuchsia-400">{aiTokens}</div>
             <div className="text-[10px] uppercase text-slate-400">AI Tokens</div>
         </div>
         <div className="flex-1">
             <div className="text-2xl font-mono text-slate-400">{manualKeys}</div>
             <div className="text-[10px] uppercase text-slate-400">Manual Keys</div>
         </div>
      </div>

      <div>
         <div className="flex justify-between text-xs mb-1">
            <span className="text-slate-400">AI Assistance Ratio</span>
            <span className="font-mono text-fuchsia-300 font-bold">{aiRatio.toFixed(1)}%</span>
         </div>
         <div className="w-full h-3 bg-slate-800 rounded-full overflow-hidden flex">
            <div 
              className="h-full bg-fuchsia-500 transition-all duration-500"
              style={{ width: `${aiRatio}%` }}
            ></div>
            <div 
              className="h-full bg-slate-600 transition-all duration-500"
              style={{ width: `${100 - aiRatio}%` }}
            ></div>
         </div>
      </div>
      
      <div className="mt-4 p-2 bg-slate-950 border border-slate-800 rounded text-[10px] text-slate-500 font-mono flex items-center gap-2">
         <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full"></div>
         Live telemetry socket connected (GDPR scrubbed)
      </div>
    </div>
  );
};
