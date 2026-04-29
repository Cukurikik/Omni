import React, { useState, useEffect } from 'react';

export const SynthController: React.FC = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [waveData, setWaveData] = useState<number[]>(Array(50).fill(0));
  const [text, setText] = useState("Initializing OMNI System...");

  useEffect(() => {
    let t = 0;
    let interval: NodeJS.Timeout;

    if (isPlaying) {
      interval = setInterval(() => {
        t += 0.2;
        // Deterministic waveform rendering
        const newWave = Array.from({ length: 50 }, (_, i) => {
          const x = i * 0.1 + t;
          return Math.sin(x) * Math.cos(x * 2.5) * 40;
        });
        setWaveData(newWave);
      }, 50);
    } else {
      setWaveData(Array(50).fill(0));
    }

    return () => clearInterval(interval);
  }, [isPlaying]);

  return (
    <div className="bg-[#121212] border border-[#2a2a2a] p-6 rounded-lg w-full max-w-2xl font-sans shadow-2xl">
      <h2 className="text-[#00ffcc] text-xl font-bold tracking-widest mb-4 uppercase">Neural TTS Synthesizer</h2>
      
      <div className="mb-4">
        <label className="block text-gray-400 text-xs mb-2 uppercase tracking-wide">Input Sequence</label>
        <textarea 
          className="w-full bg-[#1a1a1a] text-gray-200 border border-[#333] p-3 rounded focus:outline-none focus:border-[#00ffcc] transition-colors"
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={3}
        />
      </div>

      {/* Visualizer */}
      <div className="h-32 bg-[#0a0a0a] rounded border border-[#222] mb-6 flex items-center justify-center p-2 overflow-hidden relative">
        <div className="absolute inset-0 opacity-20 pointer-events-none" 
             style={{ backgroundImage: 'linear-gradient(#00ffcc 1px, transparent 1px)', backgroundSize: '100% 20px' }}>
        </div>
        
        <div className="flex items-center space-x-1 h-full z-10 w-full px-2">
          {waveData.map((val, idx) => (
            <div 
              key={idx} 
              className="flex-1 bg-[#00ffcc] rounded-full transition-all duration-75"
              style={{ 
                height: isPlaying ? `${Math.max(2, Math.abs(val))}px` : '2px',
                opacity: 0.5 + (Math.abs(val) / 80)
              }}
            />
          ))}
        </div>
      </div>

      <button 
        onClick={() => setIsPlaying(!isPlaying)}
        className={`w-full py-3 rounded font-bold uppercase tracking-wider transition-all duration-300 ${
          isPlaying 
            ? 'bg-red-500 hover:bg-red-600 text-white shadow-[0_0_15px_rgba(239,68,68,0.5)]' 
            : 'bg-[#00ffcc] hover:bg-[#33ffdb] text-[#121212] shadow-[0_0_15px_rgba(0,255,204,0.3)]'
        }`}
      >
        {isPlaying ? 'Halt Synthesis' : 'Synthesize Audio'}
      </button>
    </div>
  );
};
