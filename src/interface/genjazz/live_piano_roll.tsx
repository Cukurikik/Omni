import React, { useEffect, useRef, useState } from 'react';

// OMNI INTERFACE LAYER: Live Piano Roll
// Renders incoming MIDI notes as a scrolling piano roll.

interface NoteEvent {
  pitch: number;
  start: number; // time in ms
  duration: number; // time in ms
}

export const LivePianoRoll: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [notes, setNotes] = useState<NoteEvent[]>([]);

  useEffect(() => {
    // Zero-Mock WebSockets from Omni Concurrency Layer
    const ws = new WebSocket('ws://localhost/api/omni/genjazz/stream');
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.status === 'Ok') {
        setNotes(prev => [...prev, data.payload].slice(-100)); // Keep last 100 notes
      }
    };

    return () => ws.close();
  }, []);

  useEffect(() => {
    if (!canvasRef.current || notes.length === 0) return;
    const ctx = canvasRef.current.getContext('2d');
    if (!ctx) return;

    const width = canvasRef.current.width;
    const height = canvasRef.current.height;
    
    ctx.clearRect(0, 0, width, height);

    // Draw keyboard grid
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 1;
    for(let i=0; i<128; i++) {
      const y = height - (i / 128) * height;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    // Draw notes
    const timeRange = 5000; // view last 5 seconds
    const now = Date.now();

    notes.forEach(note => {
      const y = height - (note.pitch / 128) * height;
      const x = width - ((now - note.start) / timeRange) * width;
      const noteWidth = (note.duration / timeRange) * width;
      
      // Gradient fill for jazz aesthetic
      const gradient = ctx.createLinearGradient(x, y, x, y - 5);
      gradient.addColorStop(0, '#ff00cc');
      gradient.addColorStop(1, '#3333ff');

      ctx.fillStyle = gradient;
      ctx.fillRect(x, y - 4, noteWidth, 8);
      ctx.strokeStyle = '#fff';
      ctx.strokeRect(x, y - 4, noteWidth, 8);
    });

  }, [notes]);

  return (
    <div className="p-8 bg-black min-h-screen font-sans">
      <h1 className="text-4xl font-black italic tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-fuchsia-500 to-cyan-500 mb-6">
        OMNI DEEP JAZZ
      </h1>
      
      <div className="border border-slate-800 rounded-xl overflow-hidden shadow-[0_0_50px_rgba(255,0,255,0.1)] relative">
        <canvas ref={canvasRef} width={1000} height={500} className="w-full h-auto bg-slate-950" />
        {notes.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-slate-500 animate-pulse font-mono tracking-widest">Waiting for LSTM inference...</span>
          </div>
        )}
      </div>
      
      <div className="mt-8 flex justify-between text-slate-500 font-mono text-xs uppercase tracking-widest">
        <span>LSTM Network</span>
        <span>C++ Sine Synth FFI</span>
        <span>Elixir Concurrency</span>
      </div>
    </div>
  );
};
