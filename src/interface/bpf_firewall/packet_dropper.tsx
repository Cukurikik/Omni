import React, { useState, useEffect } from 'react';

export const PacketDropper: React.FC = () => {
  const [stats, setStats] = useState({ passed: 0, dropped: 0 });
  const [latest, setLatest] = useState<{ip: string, action: string}[]>([]);

  useEffect(() => {
    const interval = setInterval(() => {
      // Deterministic simulation
      const isDrop = Math.random() > 0.8;
      const ip = `192.168.1.${Math.floor(Math.random() * 255)}`;
      
      setStats(s => ({
        passed: s.passed + (isDrop ? 0 : 1),
        dropped: s.dropped + (isDrop ? 1 : 0)
      }));

      setLatest(prev => {
        return [{ ip, action: isDrop ? 'XDP_DROP' : 'XDP_PASS' }, ...prev].slice(0, 6);
      });
    }, 400);

    return () => clearInterval(interval);
  }, []);

  const total = stats.passed + stats.dropped || 1;
  const dropRate = ((stats.dropped / total) * 100).toFixed(1);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 border-b border-slate-700 pb-2 flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-red-500">eBPF Firewall</h2>
          <p className="text-xs text-slate-400">XDP Packet Verdicts</p>
        </div>
        <div className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_#10b981]"></div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-slate-800 p-3 rounded border border-slate-700 text-center">
          <div className="text-[10px] text-slate-400 uppercase">Passed</div>
          <div className="text-xl font-mono font-bold text-emerald-400">{stats.passed}</div>
        </div>
        <div className="bg-slate-800 p-3 rounded border border-slate-700 text-center relative overflow-hidden">
          <div className="text-[10px] text-slate-400 uppercase">Dropped</div>
          <div className="text-xl font-mono font-bold text-red-500">{stats.dropped}</div>
          <div className="absolute bottom-0 left-0 right-0 h-1 bg-red-900">
            <div className="h-full bg-red-500" style={{width: `${dropRate}%`}}></div>
          </div>
        </div>
      </div>

      <div className="flex flex-col gap-1">
        {latest.map((l, i) => (
          <div key={i} className="flex justify-between items-center bg-slate-800/50 px-3 py-2 rounded border border-slate-700/50">
            <div className="font-mono text-xs text-slate-300">{l.ip}</div>
            <div className={`text-[10px] font-bold px-1.5 py-0.5 rounded
              ${l.action === 'XDP_PASS' ? 'text-emerald-400 bg-emerald-900/30' : 'text-red-400 bg-red-900/30'}
            `}>
              {l.action}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
