import React, { useState, useEffect } from 'react';

export const DocumentViewer: React.FC = () => {
  const [parseProgress, setParseProgress] = useState(0);
  const [extractedLines, setExtractedLines] = useState<string[]>([]);
  const [layoutMode, setLayoutMode] = useState<'raw' | 'clustered'>('raw');

  useEffect(() => {
    if (parseProgress >= 100) return;

    const timer = setInterval(() => {
      setParseProgress(prev => {
        const next = prev + 5;
        if (next >= 100) {
          clearInterval(timer);
          // Deterministic simulated output
          setExtractedLines([
            "OMNI Framework Operations Manual",
            "Batch 23: Document AI Extractor",
            "1. Introduction to Layout Parsing",
            "Mathematical bounding box clustering allows",
            "for deterministic text sequence alignment."
          ]);
          return 100;
        }
        return next;
      });
    }, 100);

    return () => clearInterval(timer);
  }, [parseProgress]);

  return (
    <div className="bg-zinc-900 text-zinc-300 p-6 rounded-lg shadow-2xl max-w-2xl mx-auto font-sans border border-zinc-700">
      <div className="flex items-center justify-between border-b border-zinc-800 pb-4 mb-6">
        <h2 className="text-xl font-bold text-sky-400">Docling Layout Extractor</h2>
        <div className="flex space-x-2">
          <button 
            onClick={() => setLayoutMode('raw')}
            className={`px-3 py-1 text-xs rounded transition-colors ${layoutMode === 'raw' ? 'bg-sky-600 text-white' : 'bg-zinc-800 hover:bg-zinc-700'}`}
          >
            Raw OCR
          </button>
          <button 
            onClick={() => setLayoutMode('clustered')}
            className={`px-3 py-1 text-xs rounded transition-colors ${layoutMode === 'clustered' ? 'bg-sky-600 text-white' : 'bg-zinc-800 hover:bg-zinc-700'}`}
          >
            Clustered
          </button>
        </div>
      </div>

      <div className="bg-zinc-950 p-4 rounded border border-zinc-800 h-64 overflow-y-auto mb-6 relative">
        {parseProgress < 100 ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <div className="w-48 h-2 bg-zinc-800 rounded-full overflow-hidden mb-2">
              <div 
                className="h-full bg-sky-500 transition-all duration-100 ease-linear"
                style={{ width: `${parseProgress}%` }}
              />
            </div>
            <span className="text-xs text-zinc-500">Binarizing and Clustering ({parseProgress}%)</span>
          </div>
        ) : (
          <div className="space-y-3">
            {extractedLines.map((line, idx) => (
              <div key={idx} className="flex items-start">
                {layoutMode === 'clustered' && (
                  <span className="inline-block w-8 text-xs text-zinc-600 pt-1">[{idx}]</span>
                )}
                <div className={`flex-1 ${idx === 0 ? 'text-lg font-bold text-zinc-100' : idx === 1 ? 'text-sm font-semibold text-zinc-400' : 'text-sm text-zinc-300'}`}>
                  {layoutMode === 'clustered' ? (
                    <span className="bg-sky-900/20 border border-sky-800/30 px-2 py-0.5 rounded block">
                      {line}
                    </span>
                  ) : (
                    line
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="flex justify-between text-xs text-zinc-500">
        <span>Engine: Otsu Binarization + Y-Tolerance Clustering</span>
        <span>Confidence: 98.4%</span>
      </div>
    </div>
  );
};
