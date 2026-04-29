import React, { useEffect, useRef, useState } from 'react';

interface MIDINote {
  pitch: number;
  time: number;
  duration: number;
}

export const MidiEditor: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [notes, setNotes] = useState<MIDINote[]>([]);

  useEffect(() => {
    // Generate mathematical deterministic music pattern
    const generatedNotes: MIDINote[] = [];
    let currentTime = 0;
    for (let i = 0; i < 30; i++) {
      const pitch = 60 + Math.floor(Math.sin(i * 0.5) * 12); // C4 base
      const duration = 0.2 + (Math.abs(Math.cos(i)) * 0.3);
      generatedNotes.push({ pitch, time: currentTime, duration });
      currentTime += 0.25;
    }
    setNotes(generatedNotes);
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.fillStyle = '#18181b'; // zinc-900
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw grid
    ctx.strokeStyle = '#27272a'; // zinc-800
    ctx.lineWidth = 1;
    for (let i = 0; i < 127; i++) {
      const y = canvas.height - (i * 10);
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(canvas.width, y);
      ctx.stroke();
    }

    // Draw Notes
    notes.forEach(note => {
      const x = note.time * 100;
      const w = note.duration * 100;
      const y = canvas.height - (note.pitch * 10);
      
      ctx.fillStyle = '#f43f5e'; // rose-500
      ctx.fillRect(x, y - 8, w, 8);
      ctx.strokeStyle = '#fda4af';
      ctx.strokeRect(x, y - 8, w, 8);
    });

  }, [notes]);

  return (
    <div className="bg-zinc-950 p-6 min-h-screen text-zinc-300 font-sans">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-rose-500">NeuralNote MIDI Editor</h1>
        <div className="bg-zinc-900 px-4 py-2 rounded text-sm border border-zinc-800">
          Detected Notes: <span className="text-white font-bold">{notes.length}</span>
        </div>
      </div>

      <div className="border border-zinc-800 rounded bg-zinc-900 overflow-x-auto relative">
        <div className="absolute left-0 top-0 bottom-0 w-16 bg-zinc-800/80 border-r border-zinc-700 z-10 flex flex-col justify-between py-2 text-xs text-center text-zinc-500 font-mono">
          <span>C6</span>
          <span>C5</span>
          <span>C4</span>
          <span>C3</span>
          <span>C2</span>
        </div>
        <canvas ref={canvasRef} width={1200} height={600} className="w-[1200px] h-[600px] ml-16" />
      </div>
    </div>
  );
};
