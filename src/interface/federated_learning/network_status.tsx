import React, { useState, useEffect } from 'react';

export const NetworkStatus: React.FC = () => {
  const [round, setRound] = useState(1);
  const [activeClients, setActiveClients] = useState(0);
  const [phase, setPhase] = useState("Idle");

  useEffect(() => {
    let t = 0;
    const interval = setInterval(() => {
      t++;
      const cycle = t % 100;
      
      // Deterministic state machine for FL Rounds
      if (cycle === 0) {
        setRound(r => r + 1);
        setPhase("Selecting Clients");
        setActiveClients(Math.floor(Math.abs(Math.sin(t)) * 50) + 10);
      } else if (cycle === 20) {
        setPhase("Broadcasting Model");
      } else if (cycle === 40) {
        setPhase("Local Training");
      } else if (cycle === 70) {
        setPhase("Secure Aggregation");
      } else if (cycle === 90) {
        setPhase("Updating Global Model");
      }
      
    }, 100);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-[#0f172a] text-white p-8 rounded-xl shadow-[0_0_30px_rgba(56,189,248,0.1)] border border-[#1e293b] font-sans max-w-2xl mx-auto">
      <div className="flex justify-between items-end border-b border-[#334155] pb-4 mb-6">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-[#38bdf8]">Federated Learning Network</h2>
          <p className="text-sm text-gray-400 mt-1">Global Model Synchronization Status</p>
        </div>
        <div className="text-right">
          <div className="text-xs text-gray-500 uppercase tracking-widest mb-1">Global Round</div>
          <div className="text-3xl font-mono font-bold text-[#e2e8f0]">{String(round).padStart(4, '0')}</div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6 mb-8">
        <div className="bg-[#1e293b] p-4 rounded-lg border border-[#334155]">
          <div className="text-xs text-gray-400 uppercase tracking-wider mb-2">Active Clients</div>
          <div className="text-4xl font-bold text-[#4ade80]">{activeClients}</div>
        </div>
        
        <div className="bg-[#1e293b] p-4 rounded-lg border border-[#334155]">
          <div className="text-xs text-gray-400 uppercase tracking-wider mb-2">Current Phase</div>
          <div className="text-lg font-bold text-[#facc15] h-10 flex items-center">{phase}</div>
        </div>
      </div>

      <div className="relative pt-6">
        <div className="flex mb-2 items-center justify-between">
          <div>
            <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-blue-600 bg-blue-200">
              Round Progress
            </span>
          </div>
          <div className="text-right">
            <span className="text-xs font-semibold inline-block text-blue-300">
              {phase === "Idle" ? 100 : ((['Selecting Clients', 'Broadcasting Model', 'Local Training', 'Secure Aggregation', 'Updating Global Model'].indexOf(phase) + 1) * 20)}%
            </span>
          </div>
        </div>
        <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-[#334155]">
          <div 
            style={{ width: `${phase === "Idle" ? 100 : ((['Selecting Clients', 'Broadcasting Model', 'Local Training', 'Secure Aggregation', 'Updating Global Model'].indexOf(phase) + 1) * 20)}%` }} 
            className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-[#38bdf8] transition-all duration-300"
          ></div>
        </div>
      </div>
    </div>
  );
};
