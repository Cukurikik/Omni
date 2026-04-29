import React, { useState, useEffect } from 'react';

interface NodeStatus {
  id: string;
  epsilon: number;
  lastUpdate: string;
  status: 'Syncing' | 'Idle' | 'Encrypting';
}

export const FederatedDashboard: React.FC = () => {
  const [nodes, setNodes] = useState<NodeStatus[]>([
    { id: 'hosp-alpha-01', epsilon: 0.1, lastUpdate: new Date().toISOString(), status: 'Idle' },
    { id: 'hosp-beta-02', epsilon: 0.15, lastUpdate: new Date().toISOString(), status: 'Syncing' },
    { id: 'clinic-gamma-03', epsilon: 0.2, lastUpdate: new Date().toISOString(), status: 'Encrypting' },
  ]);

  const [globalRounds, setGlobalRounds] = useState(14);
  const [encryptionOverhead, setEncryptionOverhead] = useState(42.5);

  useEffect(() => {
    const timer = setInterval(() => {
      setNodes(prev => prev.map(n => ({
        ...n,
        status: Math.random() > 0.6 ? 'Syncing' : (Math.random() > 0.5 ? 'Encrypting' : 'Idle'),
        lastUpdate: new Date().toISOString()
      })));
      setGlobalRounds(r => r + (Math.random() > 0.9 ? 1 : 0));
      setEncryptionOverhead(e => Number((e + (Math.random() - 0.5)).toFixed(2)));
    }, 2000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-300 p-8 font-sans">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-light text-indigo-400 mb-8 border-b border-slate-800 pb-4">
          Privacy-Preserving Federated Network
        </h1>

        <div className="grid grid-cols-2 gap-8 mb-8">
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-lg shadow-xl">
            <h2 className="text-xl text-slate-500 mb-2">Global Training Rounds</h2>
            <div className="text-5xl font-mono text-indigo-300">{globalRounds}</div>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-lg shadow-xl">
            <h2 className="text-xl text-slate-500 mb-2">HE Computation Overhead</h2>
            <div className="text-5xl font-mono text-fuchsia-400">{encryptionOverhead} ms</div>
          </div>
        </div>

        <h3 className="text-2xl text-slate-400 mb-4">Active Edge Nodes</h3>
        <div className="bg-slate-900 rounded-lg overflow-hidden border border-slate-800 shadow-2xl">
          <table className="w-full text-left">
            <thead className="bg-slate-800 text-slate-400">
              <tr>
                <th className="p-4 font-medium">Node ID</th>
                <th className="p-4 font-medium">Privacy Budget (ε)</th>
                <th className="p-4 font-medium">State</th>
                <th className="p-4 font-medium">Last Ping</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {nodes.map(n => (
                <tr key={n.id} className="hover:bg-slate-800/50 transition-colors">
                  <td className="p-4 font-mono text-indigo-200">{n.id}</td>
                  <td className="p-4 font-mono">{n.epsilon}</td>
                  <td className="p-4">
                    <span className={`px-3 py-1 rounded-full text-sm ${
                      n.status === 'Syncing' ? 'bg-emerald-900/50 text-emerald-400' :
                      n.status === 'Encrypting' ? 'bg-fuchsia-900/50 text-fuchsia-400' :
                      'bg-slate-800 text-slate-400'
                    }`}>
                      {n.status}
                    </span>
                  </td>
                  <td className="p-4 text-slate-500 text-sm">{n.lastUpdate.split('T')[1].split('.')[0]}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
