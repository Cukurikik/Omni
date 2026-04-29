import React, { useState, useEffect } from 'react';

export const LeaderViz: React.FC = () => {
  const [nodes, setNodes] = useState<{id: number, state: string, term: number, heartbeat: number}[]>([
    { id: 1, state: 'LEADER', term: 4, heartbeat: 100 },
    { id: 2, state: 'FOLLOWER', term: 4, heartbeat: 100 },
    { id: 3, state: 'FOLLOWER', term: 4, heartbeat: 100 },
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      setNodes(prev => {
        let next = [...prev];
        const leader = next.find(n => n.state === 'LEADER');
        
        if (leader) {
          // Leader sends heartbeats
          next = next.map(n => ({...n, heartbeat: 100}));
          
          // Random leader crash
          if (Math.random() > 0.95) {
             const idx = next.findIndex(n => n.id === leader.id);
             next[idx].state = 'CRASHED';
             next[idx].heartbeat = 0;
          }
        } else {
          // No leader, heartbeat decays
          next = next.map(n => {
            if (n.state === 'CRASHED') {
               // Eventually recover
               if (Math.random() > 0.8) return {...n, state: 'FOLLOWER', term: n.term, heartbeat: 50};
               return n;
            }
            
            const newHb = n.heartbeat - 20;
            if (newHb <= 0) {
              // Timeout reached, become candidate
              return { ...n, state: 'CANDIDATE', term: n.term + 1, heartbeat: 100 };
            }
            return { ...n, heartbeat: newHb };
          });
          
          // If candidates exist, elect one deterministically (lowest ID wins for sim)
          const candidates = next.filter(n => n.state === 'CANDIDATE');
          if (candidates.length > 0) {
            candidates.sort((a,b) => a.id - b.id);
            const winner = candidates[0];
            next = next.map(n => {
              if (n.id === winner.id) return {...n, state: 'LEADER', heartbeat: 100};
              if (n.state === 'CANDIDATE' || n.state === 'FOLLOWER') return {...n, state: 'FOLLOWER', term: winner.term, heartbeat: 100};
              return n;
            });
          }
        }
        
        return next;
      });
    }, 500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 flex justify-between items-center border-b border-slate-700 pb-3">
        <div>
          <h2 className="text-xl font-bold text-sky-400">Raft Consensus</h2>
          <p className="text-xs text-slate-400">Leader Election Protocol</p>
        </div>
      </div>

      <div className="flex flex-col gap-3">
        {nodes.map(n => (
          <div key={n.id} className={`p-4 rounded border shadow-sm relative overflow-hidden transition-colors duration-300
            ${n.state === 'LEADER' ? 'bg-sky-900/50 border-sky-500' : 
              n.state === 'CANDIDATE' ? 'bg-amber-900/50 border-amber-500' :
              n.state === 'CRASHED' ? 'bg-rose-900/50 border-rose-500 opacity-50' :
              'bg-slate-800 border-slate-700'}
          `}>
            {/* Heartbeat timer background */}
            <div className={`absolute bottom-0 left-0 right-0 h-1 bg-slate-900/50`}>
               <div className={`h-full transition-all duration-300 ${n.state === 'LEADER' ? 'bg-sky-400 w-full' : 'bg-emerald-400'}`} style={{width: `${n.state === 'LEADER' ? 100 : n.heartbeat}%`}}></div>
            </div>

            <div className="flex justify-between items-center relative z-10">
              <div className="flex items-center gap-3">
                <div className="w-6 h-6 rounded-full bg-slate-950 flex items-center justify-center font-bold text-xs">
                  {n.id}
                </div>
                <div className="font-bold text-sm tracking-wide">
                  {n.state}
                </div>
              </div>
              <div className="text-xs font-mono font-bold text-slate-400">
                Term {n.term}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
