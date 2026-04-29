import React, { useState, useEffect } from 'react';

export const WaveformViewer: React.FC = () => {
  const [frames, setFrames] = useState<number[]>(Array(50).fill(0));
  const [vocals, setVocals] = useState<number[]>(Array(50).fill(0));
  const [accomp, setAccomp] = useState<number[]>(Array(50).fill(0));

  useEffect(() => {
    let t = 0;
    const interval = setInterval(() => {
      t += 0.1;
      
      // Deterministic signal generation to visualize
      const mixedSignal = Math.sin(t * 2) * 0.5 + Math.sin(t * 8) * 0.3;
      const vocalSignal = Math.sin(t * 2) * 0.5; // low freq sim
      const accompSignal = Math.sin(t * 8) * 0.3; // high freq sim

      setFrames(prev => [...prev.slice(1), mixedSignal]);
      setVocals(prev => [...prev.slice(1), vocalSignal]);
      setAccomp(prev => [...prev.slice(1), accompSignal]);

    }, 50);

    return () => clearInterval(interval);
  }, []);

  const renderWave = (data: number[], color: string, label: string) => (
    <div className="mb-4">
      <div className="flex justify-between items-center mb-1">
        <span className={`text-[10px] font-bold ${color}`}>{label}</span>
        <span className="text-[10px] text-zinc-500 font-mono">STFT Frame Stream</span>
      </div>
      <div className="h-16 flex items-center gap-[1px] bg-zinc-950 p-1 border border-zinc-800 rounded">
        {data.map((v, i) => {
          const height = Math.abs(v) * 100;
          return (
            <div 
              key={i} 
              className={`flex-1 ${color.replace('text-', 'bg-')} transition-all duration-75`}
              style={{ height: `${Math.max(2, height)}%` }}
            />
          );
        })}
      </div>
    </div>
  );

  return (
    <div className="bg-zinc-900 p-6 rounded border border-zinc-700 shadow-xl max-w-lg mx-auto font-sans">
      <div className="mb-6 border-b border-zinc-700 pb-2">
        <h2 className="text-xl font-bold text-cyan-500">Spleeter Tensor Waveform</h2>
        <p className="text-xs text-zinc-400">Zero-Mock Audio Separation</p>
      </div>

      {renderWave(frames, 'text-zinc-300', 'Original Mix')}
      {renderWave(vocals, 'text-fuchsia-500', 'Vocal Stem (Extracted)')}
      {renderWave(accomp, 'text-cyan-500', 'Accompaniment Stem (Extracted)')}
      
    </div>
  );
};
