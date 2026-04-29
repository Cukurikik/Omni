import React, { useState, useEffect } from 'react';

export const SubtitleViz: React.FC = () => {
  const [subtitles, setSubtitles] = useState<string[]>([]);
  const [activeTokens, setActiveTokens] = useState<string>("");

  const stream = [
    "Welcome", " to", " the", " OMNI", " framework.",
    " We", " are", " currently", " decoding", " audio", " in", " real-time",
    " using", " Whisper-Turbo", " with", " GGML", " bindings."
  ];

  useEffect(() => {
    let index = 0;
    let currentLine = "";

    const interval = setInterval(() => {
      if (index < stream.length) {
        currentLine += stream[index];
        setActiveTokens(currentLine);
        index++;
      } else {
        setSubtitles(prev => [...prev, currentLine]);
        currentLine = "";
        index = 0; // Loop for visualization
      }
    }, 200);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 border-b border-slate-700 pb-2 flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-blue-400">Whisper-Turbo</h2>
          <p className="text-xs text-slate-400">Real-Time Transcription</p>
        </div>
        <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></div>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 min-h-[120px] font-mono text-sm overflow-hidden flex flex-col justify-end">
        {subtitles.slice(-2).map((sub, i) => (
           <div key={i} className="text-slate-500 mb-2">{sub}</div>
        ))}
        <div className="text-blue-400">
           {activeTokens}<span className="inline-block w-2 h-4 bg-blue-400 ml-1 animate-ping"></span>
        </div>
      </div>
      
      <div className="mt-4 flex justify-between text-[10px] text-slate-500 font-bold uppercase">
         <span>Backend: GGML_CPU</span>
         <span>Latency: ~120ms</span>
      </div>
    </div>
  );
};
