import React, { useState, useEffect } from 'react';

export const EntropyDashboard: React.FC = () => {
  const [passwords, setPasswords] = useState<{str: string, entropy: number}[]>([]);

  useEffect(() => {
    let count = 0;
    const interval = setInterval(() => {
      count++;
      
      // Deterministic password UI population
      const len = 8 + (count % 6);
      const entropy = len * 4.5 + Math.sin(count) * 10;
      const fakePass = Array.from({length: len}, (_, i) => String.fromCharCode(65 + ((count * 13 + i * 7) % 50))).join('');

      setPasswords(prev => {
        const next = [{str: fakePass, entropy}, ...prev];
        return next.slice(0, 8); // Keep last 8
      });
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-md mx-auto font-sans text-slate-200">
      <div className="mb-6 border-b border-slate-800 pb-4">
        <h2 className="text-xl font-bold text-fuchsia-400">PassGAN Monitor</h2>
        <p className="text-xs text-slate-500">Real-time Entropy Evaluator</p>
      </div>

      <div className="space-y-3">
        {passwords.map((pw, i) => (
          <div key={i} className="flex items-center justify-between bg-slate-950 p-3 rounded border border-slate-800">
            <div className="font-mono text-slate-300 tracking-wider">
              {pw.str.replace(/./g, (c, idx) => idx < 3 ? c : '*')} {/* Masking */}
            </div>
            
            <div className="flex items-center gap-3">
              <div className="w-24 h-2 bg-slate-800 rounded overflow-hidden">
                <div 
                  className={`h-full ${pw.entropy > 50 ? 'bg-emerald-500' : 'bg-rose-500'} transition-all`}
                  style={{ width: `${Math.min(100, (pw.entropy / 80) * 100)}%` }}
                ></div>
              </div>
              <div className="text-xs font-mono text-slate-400 w-12 text-right">
                {pw.entropy.toFixed(1)}b
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-6 pt-4 border-t border-slate-800 flex justify-between text-xs text-slate-500">
        <span>Policy: Minimum 50 bits</span>
        <span className="text-fuchsia-500/50">WGAN-GP Linked</span>
      </div>
    </div>
  );
};
