import React, { useState, useEffect } from 'react';

export const AgentDashboard: React.FC = () => {
  const [contextCapacity, setContextCapacity] = useState(0);
  const [learningEvents, setLearningEvents] = useState<{id: string, impact: number}[]>([]);

  useEffect(() => {
    let tick = 0;
    const interval = setInterval(() => {
      tick++;
      
      // Deterministic simulation of agent context capacity expanding over time
      setContextCapacity(prev => Math.min(100, prev + (100 - prev) * 0.05));

      if (tick % 5 === 0) {
        setLearningEvents(prev => {
          const newEvent = {
            id: `CTX-EXP-${tick}`,
            impact: Number((Math.sin(tick) * 0.4 + 0.5).toFixed(2)) // 0.1 to 0.9 deterministic
          };
          return [newEvent, ...prev].slice(0, 5);
        });
      }
    }, 500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-[#0f172a] p-6 rounded-xl shadow-2xl border border-[#1e293b] font-sans text-gray-200 w-full max-w-lg">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-[#38bdf8] flex items-center gap-2">
          <span className="animate-pulse w-2 h-2 bg-[#38bdf8] rounded-full"></span>
          Agentic Context Engine
        </h2>
        <div className="text-xs font-mono bg-[#1e293b] px-2 py-1 rounded">LIVE</div>
      </div>

      <div className="mb-6">
        <div className="flex justify-between text-xs text-gray-400 mb-1">
          <span>Context Memory Capacity</span>
          <span>{contextCapacity.toFixed(1)}%</span>
        </div>
        <div className="h-2 w-full bg-[#1e293b] rounded-full overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-[#38bdf8] to-[#818cf8] transition-all duration-500 ease-out"
            style={{ width: `${contextCapacity}%` }}
          />
        </div>
      </div>

      <div className="bg-[#1e293b] rounded p-4">
        <h3 className="text-xs uppercase tracking-wider text-gray-500 mb-3">Recent Experiences</h3>
        <div className="space-y-2">
          {learningEvents.length === 0 ? (
            <div className="text-sm text-gray-600 text-center py-2">Waiting for events...</div>
          ) : (
            learningEvents.map(ev => (
              <div key={ev.id} className="flex justify-between items-center text-sm border-b border-[#334155] last:border-0 pb-2 last:pb-0">
                <span className="font-mono text-gray-300">{ev.id}</span>
                <span className={`font-bold ${ev.impact > 0.6 ? 'text-green-400' : 'text-blue-400'}`}>
                  +{ev.impact} impact
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
