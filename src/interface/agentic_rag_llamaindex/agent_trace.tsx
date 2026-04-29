import React, { useState, useEffect } from 'react';

export const AgentTrace: React.FC = () => {
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    const sequence = [
      "User: What is the company's Q3 revenue?",
      "Agent: [Thought] I need to query the financial database.",
      "Agent: [Action] Call Tool: query_sql_db(query='SELECT sum(revenue) FROM financials WHERE quarter=3')",
      "System: [Observation] Result: $45.2M",
      "Agent: [Thought] I have the revenue, now I formulate the answer.",
      "Agent: [Final Answer] The company's Q3 revenue was $45.2M."
    ];

    let i = 0;
    const interval = setInterval(() => {
      if (i < sequence.length) {
        setLogs(prev => [...prev, sequence[i]]);
        i++;
      } else {
        clearInterval(interval);
      }
    }, 800);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-yellow-400">LlamaIndex Agent</h2>
        <p className="text-xs text-slate-400">ReAct Reasoning Trace</p>
      </div>

      <div className="bg-black p-3 rounded border border-slate-800 h-48 overflow-y-auto font-mono text-xs space-y-2">
        {logs.map((log, i) => {
          let colorClass = "text-slate-300";
          if (log.includes("[Thought]")) colorClass = "text-fuchsia-400";
          if (log.includes("[Action]")) colorClass = "text-cyan-400";
          if (log.includes("[Observation]")) colorClass = "text-emerald-400";
          if (log.includes("[Final Answer]")) colorClass = "text-yellow-400 font-bold";
          
          return (
            <div key={i} className={`border-l-2 border-slate-700 pl-2 ${colorClass}`}>
              {log}
            </div>
          );
        })}
        {logs.length < 6 && (
           <div className="border-l-2 border-slate-700 pl-2 text-slate-500 animate-pulse">
             Agent is thinking...
           </div>
        )}
      </div>
    </div>
  );
};
