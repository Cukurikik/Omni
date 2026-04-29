import React, { useState, useEffect } from 'react';

export const SniInspector: React.FC = () => {
  const [streams, setStreams] = useState<{ip: string, sni: string, action: string}[]>([]);
  const blocked = ['malware.com', 'tracker.net'];

  useEffect(() => {
    const interval = setInterval(() => {
      const domains = ['google.com', 'github.com', 'api.stripe.com', 'malware.com', 'omniframework.dev', 'tracker.net'];
      const sni = domains[Math.floor(Math.random() * domains.length)];
      const ip = `10.0.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`;
      
      const action = blocked.includes(sni) ? 'DROP' : 'PASS';

      setStreams(prev => [{ ip, sni, action }, ...prev].slice(0, 8));
    }, 400);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-lg mx-auto font-sans text-slate-200">
      <div className="mb-6 border-b border-slate-700 pb-2 flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-teal-400">DPI TLS Inspector</h2>
          <p className="text-xs text-slate-400">Zero-Copy SNI Extraction</p>
        </div>
        <div className="text-[10px] bg-slate-800 px-2 py-1 rounded font-bold text-slate-400 border border-slate-700">
          TCP REASSEMBLY: OK
        </div>
      </div>

      <table className="w-full text-left text-xs font-mono">
        <thead className="text-slate-500 border-b border-slate-800">
          <tr>
            <th className="pb-2">Client IP</th>
            <th className="pb-2">SNI (Server Name)</th>
            <th className="pb-2 text-right">Verdict</th>
          </tr>
        </thead>
        <tbody>
          {streams.map((s, i) => (
            <tr key={i} className="border-b border-slate-800/50">
              <td className="py-2 text-slate-400">{s.ip}</td>
              <td className={`py-2 font-bold ${s.action === 'DROP' ? 'text-rose-500' : 'text-teal-400'}`}>
                {s.sni}
              </td>
              <td className="py-2 text-right">
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold
                  ${s.action === 'DROP' ? 'bg-rose-900/50 text-rose-400' : 'bg-teal-900/50 text-teal-400'}
                `}>
                  {s.action}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
