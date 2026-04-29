import React, { useState, useEffect } from 'react';

export const MonologueViz: React.FC = () => {
  const [logs, setLogs] = useState<{type: string, text: string}[]>([]);

  useEffect(() => {
    const trace = [
      { type: 'THOUGHT', text: 'I need to find the company revenue for Q3.' },
      { type: 'ACTION', text: 'Call tool: [SearchDatabase(query="Q3 Revenue")]' },
      { type: 'OBSERVATION', text: 'Result: Q3 revenue was $4.2B, up 12%.' },
      { type: 'THOUGHT', text: 'I now have the revenue. I need to format the final answer.' },
      { type: 'ACTION', text: 'Call tool: [ReturnAnswer(answer="$4.2B")]' }
    ];

    let i = 0;
    const interval = setInterval(() => {
      if (i < trace.length) {
        setLogs(prev => [...prev, trace[i]]);
        i++;
      } else {
        clearInterval(interval);
      }
    }, 1500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-blue-400">ReAct Loop</h2>
          <p className="text-xs text-slate-400">Agent Internal Monologue</p>
        </div>
        <div className="w-3 h-3 rounded-full bg-blue-500 animate-ping"></div>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 min-h-[200px] flex flex-col gap-2 font-mono text-xs">
        {logs.map((log, i) => (
          <div key={i} className={`p-2 rounded border-l-2 animate-fade-in ${
             log.type === 'THOUGHT' ? 'border-purple-500 bg-purple-900/20 text-purple-200' :
             log.type === 'ACTION' ? 'border-amber-500 bg-amber-900/20 text-amber-200 font-bold' :
             'border-emerald-500 bg-emerald-900/20 text-emerald-200'
          }`}>
             <div className="text-[8px] opacity-50 mb-1">{log.type}</div>
             <div>{log.text}</div>
          </div>
        ))}
        {logs.length < 5 && (
           <div className="p-2 text-slate-500 animate-pulse">Generating next step...</div>
        )}
      </div>
      
      <div className="mt-3 flex justify-between text-[10px] text-slate-500">
         <span>Iterations: Math.floor(logs.length / 3)</span>
         <span>Tokens: {logs.length * 42}</span>
      </div>
    </div>
  );
};
