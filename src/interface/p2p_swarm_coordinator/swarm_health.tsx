import React, { useState, useEffect } from 'react';

export const SwarmHealth: React.FC = () => {
  const [messages, setMessages] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setMessages(prev => prev + Math.floor(Math.random() * 20 + 5));
    }, 500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-purple-400">P2P Swarm</h2>
          <p className="text-xs text-slate-400">Decentralized Intelligence</p>
        </div>
        <div className="px-2 py-1 bg-emerald-900/50 text-emerald-400 rounded text-[10px] border border-emerald-800">
          Consensus: 100%
        </div>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 h-[150px] relative overflow-hidden flex flex-wrap gap-2 justify-center items-center">
         {/* Render 24 Swarm Nodes */}
         {Array.from({ length: 24 }).map((_, i) => (
           <div 
             key={i} 
             className="w-6 h-6 rounded-md border flex items-center justify-center transition-all duration-300"
             style={{
               backgroundColor: Math.random() > 0.1 ? 'rgba(168, 85, 247, 0.2)' : 'rgba(239, 68, 68, 0.2)', // 10% chance to look "faulty" but BFT handles it
               borderColor: Math.random() > 0.1 ? 'rgba(168, 85, 247, 0.5)' : 'rgba(239, 68, 68, 0.5)',
               transform: `scale(${0.8 + Math.random() * 0.4})`
             }}
           >
             <div className="w-1.5 h-1.5 rounded-full bg-white opacity-50 animate-ping"></div>
           </div>
         ))}
      </div>
      
      <div className="mt-4 grid grid-cols-2 gap-4 text-center">
         <div className="bg-slate-800 p-2 rounded">
            <div className="text-xs text-slate-400 uppercase">Gossip Msg/s</div>
            <div className="font-mono text-purple-400 text-lg">{messages}</div>
         </div>
         <div className="bg-slate-800 p-2 rounded">
            <div className="text-xs text-slate-400 uppercase">Active Peers</div>
            <div className="font-mono text-emerald-400 text-lg">24/24</div>
         </div>
      </div>
    </div>
  );
};
