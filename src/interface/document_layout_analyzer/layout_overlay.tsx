import React, { useState, useEffect } from 'react';

export const LayoutOverlay: React.FC = () => {
  const [scanLine, setScanLine] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setScanLine(prev => (prev > 100 ? 0 : prev + 2));
    }, 50);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-pink-400">Layout Analyzer</h2>
        <p className="text-xs text-slate-400">PDF RAG Visual Ingestion</p>
      </div>

      <div className="bg-slate-200 p-2 rounded h-[200px] relative overflow-hidden border-2 border-slate-600">
         {/* Simulated PDF Page Document */}
         
         {/* Title Block */}
         <div className="absolute top-4 left-4 right-4 h-6 border-2 border-pink-500 bg-pink-500/20 rounded-sm">
             <div className="absolute -top-3 left-0 text-[8px] font-mono text-pink-700 bg-pink-200 px-1 rounded-t border-t border-l border-r border-pink-500">H1_TITLE</div>
         </div>
         
         {/* Paragraph Blocks */}
         <div className="absolute top-14 left-4 w-[60%] h-16 border-2 border-blue-500 bg-blue-500/20 rounded-sm">
            <div className="absolute -top-3 left-0 text-[8px] font-mono text-blue-700 bg-blue-200 px-1 rounded-t border-t border-l border-r border-blue-500">PARAGRAPH_1</div>
            {/* Mock text lines */}
            <div className="mt-1 ml-1 w-[90%] h-1 bg-slate-400 rounded"></div>
            <div className="mt-1 ml-1 w-[85%] h-1 bg-slate-400 rounded"></div>
            <div className="mt-1 ml-1 w-[95%] h-1 bg-slate-400 rounded"></div>
         </div>
         
         {/* Table Block */}
         <div className="absolute top-14 right-4 w-[30%] h-24 border-2 border-emerald-500 bg-emerald-500/20 rounded-sm flex flex-col">
            <div className="absolute -top-3 left-0 text-[8px] font-mono text-emerald-700 bg-emerald-200 px-1 rounded-t border-t border-l border-r border-emerald-500">TABLE_DATA</div>
            <div className="w-full border-b border-emerald-400 mt-2"></div>
            <div className="w-full border-b border-emerald-400 mt-2"></div>
            <div className="w-full border-b border-emerald-400 mt-2"></div>
         </div>

         {/* Image Block */}
         <div className="absolute bottom-4 left-4 right-4 h-12 border-2 border-amber-500 bg-amber-500/20 rounded-sm flex items-center justify-center">
            <div className="absolute -top-3 left-0 text-[8px] font-mono text-amber-700 bg-amber-200 px-1 rounded-t border-t border-l border-r border-amber-500">FIGURE_1</div>
            <span className="text-amber-700 text-xs font-bold">✖</span>
         </div>

         {/* Scanning Laser Effect */}
         <div 
           className="absolute left-0 right-0 h-1 bg-red-500/50 shadow-[0_0_8px_rgba(239,68,68,0.8)] z-10"
           style={{ top: `${scanLine}%` }}
         ></div>
      </div>
      
      <div className="mt-3 flex justify-between font-mono text-[10px] text-slate-500">
         <span>BBoxes Detected: 4</span>
         <span>Logical Order: Solved</span>
      </div>
    </div>
  );
};
