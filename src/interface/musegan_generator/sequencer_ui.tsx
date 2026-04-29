import React, { useState, useEffect } from 'react';

export const SequencerUI: React.FC = () => {
  const [playhead, setPlayhead] = useState(0);
  const [tracks, setTracks] = useState<number[][][]>([]);

  useEffect(() => {
    // Generate deterministic 4-bar loop across 4 tracks (Drums, Bass, Chords, Melody)
    // 16 steps per bar * 4 = 64 steps
    const numSteps = 64;
    const generated = Array.from({ length: 4 }, (_, trk) => 
      Array.from({ length: numSteps }, (_, step) => {
        const notes = [];
        // Deterministic generative math
        if (trk === 0 && step % 4 === 0) notes.push(36); // Kick
        if (trk === 0 && (step + 2) % 4 === 0) notes.push(38); // Snare
        if (trk === 1 && step % 2 === 0) notes.push(24 + Math.abs(Math.sin(step) * 12)); // Bass
        if (trk === 2 && step % 16 === 0) notes.push(60, 64, 67); // Chords
        if (trk === 3 && step % 3 === 0) notes.push(72 + Math.cos(step) * 12); // Melody
        return notes;
      })
    );
    
    setTracks(generated);

    const interval = setInterval(() => {
      setPlayhead(prev => (prev + 1) % numSteps);
    }, 150); // ~100 BPM 16th notes

    return () => clearInterval(interval);
  }, []);

  const trackColors = ['bg-rose-500', 'bg-blue-500', 'bg-emerald-500', 'bg-amber-500'];
  const trackNames = ['Drums', 'Bass', 'Chords', 'Melody'];

  return (
    <div className="bg-zinc-900 p-6 rounded-lg border border-zinc-700 shadow-2xl max-w-4xl mx-auto font-sans text-zinc-200">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-xl font-bold text-amber-400">MuseGAN Sequencer</h2>
          <p className="text-xs text-zinc-500">Multi-track Adversarial Matrix</p>
        </div>
        <div className="bg-zinc-800 px-3 py-1 rounded border border-zinc-700 text-sm font-mono text-amber-300">
          BAR: {Math.floor(playhead / 16) + 1} | BEAT: {Math.floor((playhead % 16) / 4) + 1}
        </div>
      </div>

      <div className="space-y-2 relative">
        {/* Playhead line */}
        <div 
          className="absolute top-0 bottom-0 w-0.5 bg-white/50 z-10 transition-all duration-[150ms] ease-linear"
          style={{ left: `${(playhead / 64) * 100}%` }}
        ></div>

        {tracks.map((track, trkIdx) => (
          <div key={trkIdx} className="flex h-16 bg-zinc-950 rounded border border-zinc-800 relative">
            {/* Track Header */}
            <div className="w-20 border-r border-zinc-800 bg-zinc-900 flex items-center justify-center text-xs font-bold text-zinc-500 z-20">
              {trackNames[trkIdx]}
            </div>
            
            {/* Grid */}
            <div className="flex-1 relative flex">
              {Array.from({ length: 64 }).map((_, stepIdx) => (
                <div 
                  key={stepIdx} 
                  className={`flex-1 border-r border-zinc-800/50 ${stepIdx % 4 === 0 ? 'bg-zinc-800/20' : ''}`}
                >
                  {track[stepIdx]?.map((note, nIdx) => (
                    <div 
                      key={nIdx}
                      className={`w-full h-2 mt-1 rounded-sm ${trackColors[trkIdx]} shadow-[0_0_4px_currentColor]`}
                      style={{ opacity: stepIdx === playhead ? 1 : 0.6 }}
                      title={`MIDI: ${Math.floor(note)}`}
                    ></div>
                  ))}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 flex justify-between text-xs text-zinc-500">
        <span>Quantization: Diatonic Auto-Snap</span>
        <span>Generator: Wasserstein GAN-GP</span>
      </div>
    </div>
  );
};
