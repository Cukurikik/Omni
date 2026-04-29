import React, { useState, useEffect } from 'react';

export const ClusterMonitor: React.FC = () => {
  const [activeWorkers, setActiveWorkers] = useState(0);
  const [cpuUsage, setCpuUsage] = useState(0);
  const [tasksCompleted, setTasksCompleted] = useState(0);

  useEffect(() => {
    let tick = 0;
    const interval = setInterval(() => {
      tick++;
      
      // Deterministic math logic for cluster simulation
      const baseWorkers = 50;
      const loadSpike = Math.sin(tick * 0.1) * 20;
      const currentWorkers = Math.floor(baseWorkers + loadSpike);
      
      setActiveWorkers(currentWorkers);
      setCpuUsage(Math.min(100, Math.max(10, currentWorkers * 1.2 + Math.cos(tick) * 5)));
      setTasksCompleted(prev => prev + Math.floor(currentWorkers / 10));

    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 text-slate-200 p-6 rounded-lg shadow-xl border border-slate-700 font-sans max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-8 border-b border-slate-700 pb-4">
        <h1 className="text-2xl font-bold text-emerald-400">Fugue Compute Cluster</h1>
        <div className="flex space-x-2">
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
            <span className="text-xs uppercase tracking-wider text-slate-400">Cluster Online</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6 mb-8">
        <div className="bg-slate-800 p-4 rounded border border-slate-600">
          <div className="text-sm text-slate-400 mb-1">Active Workers</div>
          <div className="text-4xl font-mono font-bold text-blue-400">{activeWorkers}</div>
        </div>
        <div className="bg-slate-800 p-4 rounded border border-slate-600 relative overflow-hidden">
          <div className="text-sm text-slate-400 mb-1">CPU Utilization</div>
          <div className="text-4xl font-mono font-bold text-amber-400">{cpuUsage.toFixed(1)}%</div>
          <div className="absolute bottom-0 left-0 h-1 bg-slate-700 w-full">
            <div className="h-full bg-amber-400 transition-all duration-500" style={{ width: `${cpuUsage}%` }}></div>
          </div>
        </div>
        <div className="bg-slate-800 p-4 rounded border border-slate-600">
          <div className="text-sm text-slate-400 mb-1">Tasks Completed</div>
          <div className="text-4xl font-mono font-bold text-purple-400">{tasksCompleted}</div>
        </div>
      </div>

      <div className="bg-slate-800 p-4 rounded border border-slate-600">
        <h3 className="text-sm font-semibold text-slate-300 mb-4 uppercase tracking-wide">Worker Node Topology</h3>
        <div className="flex flex-wrap gap-2">
          {Array.from({ length: 100 }).map((_, i) => (
            <div 
              key={i} 
              className={`w-4 h-4 rounded-sm transition-colors duration-300 ${i < activeWorkers ? 'bg-emerald-500 shadow-[0_0_5px_#10b981]' : 'bg-slate-700'}`}
              title={`Node-${i}`}
            />
          ))}
        </div>
      </div>
    </div>
  );
};
