import React, { useState, useEffect } from 'react';

export const LinkGraph: React.FC = () => {
  const [tokens, setTokens] = useState<string[]>([]);
  
  useEffect(() => {
    const rawTokens = [
      "<URL>", "https://example.com", "</URL>",
      "<H1>", "Main", "Title", "</H1>",
      "<P>", "This", "is", "the", "extracted", "text", "from", "the", "DOM", "</P>",
      "<A>", "Internal", "Link", "</A>"
    ];

    let i = 0;
    const interval = setInterval(() => {
      if (i < rawTokens.length) {
        setTokens(prev => [...prev, rawTokens[i]]);
        i++;
      } else {
        clearInterval(interval);
      }
    }, 150);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-orange-400">Linky</h2>
          <p className="text-xs text-slate-400">URL to Vector Tokenization</p>
        </div>
        <div className="text-2xl">🔗</div>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 min-h-[150px] flex flex-wrap gap-2 content-start">
        {tokens.map((token, i) => {
          const isTag = token.startsWith('<');
          return (
            <span 
              key={i} 
              className={`text-xs px-2 py-1 rounded font-mono ${
                isTag 
                  ? 'bg-orange-900/50 text-orange-400 border border-orange-700/50' 
                  : 'bg-slate-800 text-slate-300'
              } animate-fade-in`}
            >
              {token}
            </span>
          );
        })}
        {tokens.length < 18 && (
          <span className="text-xs px-2 py-1 bg-slate-800 text-slate-500 rounded font-mono animate-pulse">
            parsing...
          </span>
        )}
      </div>
      <div className="mt-2 text-right text-[10px] text-slate-500">
         Compression Ratio: 8.4x
      </div>
    </div>
  );
};
