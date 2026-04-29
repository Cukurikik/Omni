import React, { useState, useEffect } from 'react';

export const DocViewer: React.FC = () => {
  const [scanLineY, setScanLineY] = useState(0);
  const [extractedText, setExtractedText] = useState<string[]>([]);

  useEffect(() => {
    let t = 0;
    const documentLines = [
      "OMNI FRAMEWORK INVOICE",
      "Date: 2026-04-26",
      "Client: Global Nexus Corp",
      "-----------------------",
      "Service: [EMAIL REDACTED]",
      "Amount: $42,000.00",
      "Status: VERIFIED"
    ];

    const interval = setInterval(() => {
      t++;
      
      // Scanning animation 0 to 100%
      const newY = (t * 2) % 100;
      setScanLineY(newY);

      // Reveal text as scanner passes
      const linesToReveal = Math.floor((newY / 100) * documentLines.length);
      setExtractedText(documentLines.slice(0, linesToReveal + 1));

    }, 50);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-50 p-6 rounded shadow-lg max-w-2xl mx-auto font-sans flex gap-6">
      
      {/* Left: Document View */}
      <div className="flex-1 border border-slate-300 bg-white p-4 relative h-80 overflow-hidden shadow-inner">
        <div className="absolute top-4 right-4 text-xs font-bold text-slate-300">CONFIDENTIAL</div>
        
        {/* Mock Document Content */}
        <div className="space-y-4 pt-8">
          <div className="w-3/4 h-4 bg-slate-200 rounded"></div>
          <div className="w-1/2 h-3 bg-slate-100 rounded"></div>
          <div className="w-2/3 h-3 bg-slate-100 rounded"></div>
          <div className="w-full h-[1px] bg-slate-200 my-4"></div>
          <div className="w-full h-3 bg-slate-100 rounded"></div>
          <div className="w-1/3 h-3 bg-slate-200 rounded"></div>
        </div>

        {/* OCR Scan Line */}
        <div 
          className="absolute left-0 right-0 h-[2px] bg-blue-500 shadow-[0_0_8px_#3b82f6] transition-all duration-75 z-10"
          style={{ top: `${scanLineY}%` }}
        ></div>
        {/* Scanner Overlay */}
        <div 
          className="absolute left-0 right-0 top-0 bg-blue-500/10 pointer-events-none"
          style={{ height: `${scanLineY}%` }}
        ></div>
      </div>

      {/* Right: Extracted Data */}
      <div className="flex-1 bg-slate-900 rounded p-4 border border-slate-800 text-slate-300 font-mono text-sm overflow-hidden flex flex-col">
        <div className="text-blue-400 font-bold mb-3 border-b border-slate-800 pb-2 flex justify-between">
          <span>OCR_OUTPUT.txt</span>
          <span className="text-[10px] bg-blue-900/50 px-1 rounded text-blue-300">PII SAFE</span>
        </div>
        
        <div className="space-y-1 flex-1">
          {extractedText.map((line, i) => (
            <div key={i} className="animate-fade-in text-xs whitespace-pre">
              {line}
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};
