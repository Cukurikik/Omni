import React, { useState, useEffect } from 'react';

export const GenerationStream: React.FC = () => {
  const [text, setText] = useState("");
  
  const fullResponse = "Based on the retrieved context, RAG (Retrieval-Augmented Generation) enhances LLMs by connecting them to external vector databases. This significantly reduces hallucinations and provides up-to-date information without requiring expensive model fine-tuning.";

  useEffect(() => {
    let i = 0;
    const interval = setInterval(() => {
      if (i <= fullResponse.length) {
        setText(fullResponse.substring(0, i));
        i += Math.floor(Math.random() * 3) + 1; // Stream 1-3 chars at a time
      } else {
        clearInterval(interval);
      }
    }, 30); // Fast stream

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex items-center justify-between border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-white">RAG From Scratch</h2>
          <p className="text-xs text-slate-400">LLM Generation Pipeline</p>
        </div>
        <div className="flex space-x-1">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-bounce" style={{animationDelay: '0ms'}}></div>
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-bounce" style={{animationDelay: '150ms'}}></div>
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-bounce" style={{animationDelay: '300ms'}}></div>
        </div>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 min-h-[120px] font-mono text-sm text-emerald-300 leading-relaxed shadow-inner">
        {text}
        {text.length < fullResponse.length && <span className="inline-block w-2 h-4 bg-emerald-400 ml-1 animate-pulse"></span>}
      </div>
      
      <div className="mt-3 text-[10px] text-slate-500 flex justify-between">
         <span>Tokens: {Math.floor(text.length / 4)}</span>
         <span>Latency: 24ms (TTFT)</span>
      </div>
    </div>
  );
};
