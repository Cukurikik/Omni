import React, { useState, useEffect } from 'react';

export const SwarmMetrics: React.FC = () => {
  const [agents, setAgents] = useState([
    { id: 'Codex-Primary', load: 80, tasks: 12 },
    { id: 'QA-Validator', load: 30, tasks: 4 },
    { id: 'Data-Extractor', load: 95, tasks: 28 }
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      setAgents(prev => prev.map(agent => ({
        ...agent,
        // Simulate dynamic load balancing
        load: Math.max(10, Math.min(100, agent.load + (Math.random() * 20 - 10))),
        tasks: agent.load > 90 ? Math.max(0, agent.tasks - 1) : agent.tasks + (Math.random() > 0.7 ? 1 : 0)
      })));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 border-b border-slate-700 pb-2">
        <h2 className="text-xl font-bold text-purple-400">Multi-Agent Swarm</h2>
        <p className="text-xs text-slate-400">LlamaIndex Router Telemetry</p>
      </div>

      <div className="space-y-3">
        {agents.map((agent) => (
          <div key={agent.id} className="bg-slate-950 p-3 rounded border border-slate-800">
            <div className="flex justify-between items-center mb-1">
              <span className="font-mono text-xs font-bold text-slate-300">{agent.id}</span>
              <span className="text-[10px] text-slate-500">Queue: {agent.tasks}</span>
            </div>
            
            <div className="flex items-center gap-2">
               <div className="flex-1 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                  <div 
                    className={`h-full transition-all duration-500 ${agent.load > 85 ? 'bg-rose-500' : agent.load > 60 ? 'bg-amber-500' : 'bg-purple-500'}`}
                    style={{ width: `${agent.load}%` }}
                  />
               </div>
               <span className="text-[10px] font-mono w-8 text-right">{agent.load.toFixed(0)}%</span>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 flex justify-between items-center text-xs text-slate-400">
         <span>Swarm Status: <span className="text-emerald-400">Healthy</span></span>
         <span>Latency: ~12ms</span>
      </div>
    </div>
  );
};
