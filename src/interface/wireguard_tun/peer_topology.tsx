import React, { useState, useEffect } from 'react';

export const PeerTopology: React.FC = () => {
  const [peers, setPeers] = useState<{pubKey: string, endpoint: string, rx: number, tx: number, latestHandshake: number}[]>([
    { pubKey: 'xA4F...9pL2', endpoint: '198.51.100.22:51820', rx: 450, tx: 820, latestHandshake: 0 },
    { pubKey: 'vM9E...2jK8', endpoint: '203.0.113.8:58211', rx: 120, tx: 90, latestHandshake: 0 }
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      setPeers(prev => prev.map(p => {
        const dRx = Math.floor(Math.random() * 50);
        const dTx = Math.floor(Math.random() * 40);
        
        let hs = p.latestHandshake + 1;
        if (hs > 120) hs = 0; // WireGuard rotates keys roughly every ~120s of traffic

        return {
          ...p,
          rx: p.rx + dRx,
          tx: p.tx + dTx,
          latestHandshake: hs
        };
      }));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-2xl mx-auto font-sans text-slate-200">
      <div className="mb-6 flex justify-between items-center border-b border-slate-700 pb-3">
        <div>
          <h2 className="text-xl font-bold text-rose-500">WireGuard</h2>
          <p className="text-xs text-slate-400">Cryptokey Routing Topology</p>
        </div>
        <div className="text-[10px] font-mono bg-slate-800 text-slate-400 px-2 py-1 rounded">
          ChaCha20-Poly1305 AEAD
        </div>
      </div>

      <div className="flex flex-col gap-4">
        {peers.map((p, i) => (
          <div key={i} className="bg-slate-800 p-4 rounded border border-slate-700 flex flex-col gap-3 shadow-sm">
            <div className="flex justify-between items-center border-b border-slate-700 pb-2">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-rose-900/50 flex items-center justify-center text-rose-500">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 11c0 3.517-1.009 6.799-2.753 9.571m-3.44-2.04l.054-.09A13.916 13.916 0 008 11a4 4 0 118 0c0 1.017-.07 2.019-.203 3m-2.118 6.844A21.88 21.88 0 0015.171 17m3.839 1.132c.645-2.266.99-4.659.99-7.132A8 8 0 008 4h.002M8 4H4m4 0v4"></path>
                  </svg>
                </div>
                <div>
                  <div className="font-mono text-sm font-bold text-slate-300">{p.pubKey}</div>
                  <div className="text-[10px] text-slate-500 font-mono">{p.endpoint}</div>
                </div>
              </div>
              
              <div className="text-right">
                <div className="text-[10px] text-slate-500 uppercase font-bold">Latest Handshake</div>
                <div className={`text-xs font-mono font-bold ${p.latestHandshake < 5 ? 'text-emerald-400' : 'text-slate-300'}`}>
                  {p.latestHandshake === 0 ? 'Just now' : `${p.latestHandshake}s ago`}
                </div>
              </div>
            </div>
            
            <div className="flex justify-between items-center px-2">
              <div>
                <div className="text-[9px] text-slate-500 uppercase">Transfer Rx</div>
                <div className="text-sm font-mono text-emerald-400 font-bold">{(p.rx / 1024).toFixed(2)} MB</div>
              </div>
              <div className="h-0.5 w-16 bg-slate-700 relative overflow-hidden">
                <div className="absolute inset-0 bg-emerald-500/30"></div>
                <div className="absolute top-0 bottom-0 left-0 bg-emerald-500 animate-pulse" style={{width: '30%'}}></div>
              </div>
              <div className="text-right">
                <div className="text-[9px] text-slate-500 uppercase">Transfer Tx</div>
                <div className="text-sm font-mono text-rose-400 font-bold">{(p.tx / 1024).toFixed(2)} MB</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
