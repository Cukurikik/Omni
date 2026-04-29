import React, { useState, useEffect } from 'react';

export const TunnelMonitor: React.FC = () => {
  const [tunnels, setTunnels] = useState<{spi: string, peer: string, pkts: number, bytes: number, status: string}[]>([
    { spi: '0x1A2B3C4D', peer: '198.51.100.14', pkts: 0, bytes: 0, status: 'UP' },
    { spi: '0x9F8E7D6C', peer: '203.0.113.88', pkts: 0, bytes: 0, status: 'UP' },
    { spi: '0x4B5A6978', peer: '192.0.2.45', pkts: 0, bytes: 0, status: 'REKEYING' }
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      setTunnels(prev => prev.map(t => {
        if (t.status !== 'UP') {
          if (Math.random() > 0.8) return { ...t, status: 'UP' };
          return t;
        }

        const newPkts = Math.floor(Math.random() * 50);
        const newBytes = newPkts * 1420; // MTU minus IPsec overhead
        
        if (t.bytes > 1000000 && Math.random() > 0.95) {
          return { ...t, status: 'REKEYING' }; // Phase 2 rekey
        }

        return {
          ...t,
          pkts: t.pkts + newPkts,
          bytes: t.bytes + newBytes
        };
      }));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-2xl mx-auto font-sans text-slate-200">
      <div className="mb-6 flex justify-between items-center border-b border-slate-700 pb-3">
        <div>
          <h2 className="text-xl font-bold text-sky-500">IPsec VPN</h2>
          <p className="text-xs text-slate-400">ESP Tunnel Security Associations</p>
        </div>
        <div className="text-[10px] font-mono text-slate-400 bg-slate-800 px-2 py-1 rounded">
          AES-GCM-256 / SHA384
        </div>
      </div>

      <div className="overflow-hidden rounded border border-slate-700 bg-slate-950">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-800 text-slate-400 border-b border-slate-700">
            <tr>
              <th className="p-3 font-bold text-xs uppercase">SPI</th>
              <th className="p-3 font-bold text-xs uppercase">Peer IP</th>
              <th className="p-3 font-bold text-xs uppercase text-right">Packets</th>
              <th className="p-3 font-bold text-xs uppercase text-right">Data</th>
              <th className="p-3 font-bold text-xs uppercase text-center">Status</th>
            </tr>
          </thead>
          <tbody>
            {tunnels.map((t, i) => (
              <tr key={t.spi} className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors">
                <td className="p-3 font-mono text-xs text-sky-400">{t.spi}</td>
                <td className="p-3 font-mono text-xs text-slate-300">{t.peer}</td>
                <td className="p-3 text-right font-mono text-xs">{t.pkts.toLocaleString()}</td>
                <td className="p-3 text-right font-mono text-xs text-emerald-400">{(t.bytes / 1024).toFixed(1)} KB</td>
                <td className="p-3 flex justify-center">
                  <div className={`px-2 py-1 rounded text-[10px] font-bold w-20 text-center
                    ${t.status === 'UP' ? 'bg-emerald-900/50 text-emerald-400' : 'bg-amber-900/50 text-amber-400 animate-pulse'}
                  `}>
                    {t.status}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
