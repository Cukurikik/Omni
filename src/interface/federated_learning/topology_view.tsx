import React, { useState, useEffect } from 'react';

export const TopologyView: React.FC = () => {
  const [round, setRound] = useState(1);
  const [clients, setClients] = useState<{id: number, status: 'IDLE'|'TRAINING'|'UPLOADING'|'AGGREGATING'}[]>([]);

  useEffect(() => {
    // Deterministic state simulation for 5 clients
    let step = 0;
    const interval = setInterval(() => {
      step++;
      
      const newClients = Array.from({length: 5}, (_, i) => {
        // Stagger client states deterministically
        const localStep = (step + i * 2) % 20;
        let status: 'IDLE'|'TRAINING'|'UPLOADING'|'AGGREGATING' = 'IDLE';
        
        if (localStep < 10) status = 'TRAINING';
        else if (localStep < 15) status = 'UPLOADING';
        else if (localStep < 18) status = 'AGGREGATING';
        
        return { id: i, status };
      });
      
      setClients(newClients);

      if (step % 20 === 0) {
        setRound(r => r + 1);
      }
    }, 500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-xl border border-slate-700 shadow-2xl max-w-2xl mx-auto font-sans">
      <div className="flex justify-between items-center mb-8 border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-xl font-bold text-sky-400">Federated Topology</h2>
          <p className="text-xs text-slate-500">Secure Aggregation Ring</p>
        </div>
        <div className="bg-slate-800 px-3 py-1 rounded text-sm font-mono text-sky-300">
          GLOBAL ROUND: {round}
        </div>
      </div>

      <div className="relative h-64 flex items-center justify-center">
        {/* Central Server Node */}
        <div className="absolute z-20 w-16 h-16 bg-slate-800 rounded-full border-2 border-sky-500 flex items-center justify-center shadow-[0_0_20px_#0ea5e9]">
          <span className="text-xs font-bold text-sky-400 text-center leading-tight">GLOBAL<br/>MODEL</span>
        </div>

        {/* Client Nodes around Center */}
        {clients.map((client, i) => {
          const angle = (i / 5) * Math.PI * 2 - Math.PI / 2;
          const radius = 100;
          const x = Math.cos(angle) * radius;
          const y = Math.sin(angle) * radius;

          const isActive = client.status !== 'IDLE';
          const isUploading = client.status === 'UPLOADING';

          return (
            <div key={client.id} className="absolute inset-0 flex items-center justify-center z-10">
              {/* Connection Line */}
              <div 
                className={`absolute w-0.5 origin-bottom transition-colors duration-300 ${isUploading ? 'bg-sky-500 shadow-[0_0_8px_#0ea5e9]' : 'bg-slate-700'}`}
                style={{
                  height: `${radius}px`,
                  transform: `rotate(${angle + Math.PI/2}rad) translateY(-${radius/2}px)`
                }}
              ></div>
              
              {/* Client Node */}
              <div 
                className={`absolute w-12 h-12 rounded-full border-2 flex items-center justify-center transition-all duration-300 ${isActive ? 'bg-slate-800 border-indigo-400 shadow-[0_0_10px_#818cf8]' : 'bg-slate-900 border-slate-700'}`}
                style={{ transform: `translate(${x}px, ${y}px)` }}
              >
                <div className="flex flex-col items-center justify-center">
                  <span className="text-[10px] text-slate-400 font-mono">C_{client.id}</span>
                  <div className={`w-2 h-2 rounded-full mt-1 ${client.status === 'TRAINING' ? 'bg-indigo-400 animate-pulse' : client.status === 'UPLOADING' ? 'bg-sky-400' : 'bg-slate-600'}`}></div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-8 flex justify-center gap-4 text-xs font-mono text-slate-500">
        <span className="flex items-center gap-1"><div className="w-2 h-2 bg-indigo-400 rounded-full"></div> Training</span>
        <span className="flex items-center gap-1"><div className="w-2 h-2 bg-sky-400 rounded-full"></div> Uploading</span>
        <span className="flex items-center gap-1"><div className="w-2 h-2 bg-slate-600 rounded-full"></div> Idle</span>
      </div>
    </div>
  );
};
