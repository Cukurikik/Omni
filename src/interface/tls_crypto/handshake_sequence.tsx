import React, { useState, useEffect } from 'react';

export const HandshakeSequence: React.FC = () => {
  const [sequence, setSequence] = useState<{step: string, ms: number}[]>([]);

  useEffect(() => {
    let t = 0;
    const interval = setInterval(() => {
      t++;
      const steps = [
        'ClientHello',
        'ServerHello',
        'Certificate, CertificateVerify, Finished',
        'Finished (Client)',
        'Application Data (Encrypted)'
      ];
      
      const stepIdx = t % steps.length;
      if (stepIdx === 0) setSequence([]); // Reset for new handshake
      
      setSequence(prev => [
        ...prev, 
        { step: steps[stepIdx], ms: Math.floor(Math.random() * 5) + 2 }
      ]);

    }, 800);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-950 p-6 rounded-lg border border-slate-800 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 border-b border-slate-800 pb-2">
        <h2 className="text-xl font-bold text-amber-500">TLS 1.3 Crypto</h2>
        <p className="text-xs text-slate-400">1-RTT Handshake Sequence</p>
      </div>

      <div className="flex flex-col gap-3">
        {sequence.map((s, i) => (
          <div key={i} className="flex flex-col">
            <div className={`text-xs font-bold px-3 py-2 rounded border border-slate-800 shadow-sm flex justify-between items-center
              ${i % 2 === 0 ? 'bg-slate-900 self-start text-blue-400 mr-8' : 'bg-slate-800 self-end text-emerald-400 ml-8'}
            `}>
               <span>{s.step}</span>
               <span className="text-[10px] font-mono text-slate-500 ml-3">+{s.ms}ms</span>
            </div>
            
            {i < sequence.length - 1 && (
              <div className="h-4 border-l-2 border-dashed border-slate-700 ml-8"></div>
            )}
          </div>
        ))}
        {sequence.length === 0 && (
          <div className="text-center text-xs text-slate-600 mt-4 font-mono animate-pulse">Waiting for ClientHello...</div>
        )}
      </div>
    </div>
  );
};
