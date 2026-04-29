import React, { useState, useEffect } from 'react';

export const HTRViewer: React.FC = () => {
  const [scannedText, setScannedText] = useState("");
  const [confidence, setConfidence] = useState(0.0);
  const [isScanning, setIsScanning] = useState(false);

  useEffect(() => {
    let t = 0;
    let interval: NodeJS.Timeout;

    if (isScanning) {
      const sourceText = "Omni Framework Handwritten Text Engine";
      setScannedText("");
      
      interval = setInterval(() => {
        t++;
        
        if (t <= sourceText.length) {
          // Deterministic progressive revealing of text to simulate CTC decoding over time steps
          setScannedText(sourceText.substring(0, t));
          setConfidence(0.85 + Math.sin(t) * 0.1); // Mock varying confidence mathematically
        } else {
          setIsScanning(false);
          clearInterval(interval);
        }
      }, 100);
    }

    return () => clearInterval(interval);
  }, [isScanning]);

  return (
    <div className="p-8 bg-[#fafafa] rounded-md border border-[#e5e5e5] shadow-sm max-w-lg w-full font-serif text-gray-800 mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold tracking-tight">HTR System</h2>
        <button 
          onClick={() => setIsScanning(true)}
          disabled={isScanning}
          className="px-4 py-2 bg-black text-white text-sm font-sans font-bold rounded hover:bg-gray-800 disabled:opacity-50"
        >
          {isScanning ? 'Scanning...' : 'Scan Image'}
        </button>
      </div>

      {/* Simulated Image Area */}
      <div className="w-full h-24 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiPgo8cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjNmM2YzIi8+Cjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQ3Vyc2l2ZSIgZm9udC1zaXplPSIyNCIgZmlsbD0iIzQ0NCIgZmlsbC1vcGFjaXR5PSIwLjUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGFsaWdubWVudC1iYXNlbGluZT0ibWlkZGxlIj4gfiBIYW5kd3JpdHRlbiBEb2N1bWVudCB+IDwvdGV4dD4KPC9zdmc+')] bg-cover bg-center rounded border border-gray-300 mb-6 relative overflow-hidden">
        {isScanning && (
          <div className="absolute top-0 bottom-0 left-0 w-1 bg-blue-500 shadow-[0_0_8px_#3b82f6] animate-[scan_3s_linear_infinite]" style={{
            animation: `scan ${38 / 10}s linear forwards`
          }}>
            <style>{`
              @keyframes scan {
                0% { left: 0%; }
                100% { left: 100%; }
              }
            `}</style>
          </div>
        )}
      </div>

      {/* Results Area */}
      <div className="bg-white p-4 rounded border border-gray-200 min-h-[100px]">
        <div className="text-xs text-gray-500 font-sans uppercase mb-2">Transcription</div>
        <div className="text-lg font-medium min-h-[1.5rem]">
          {scannedText}
          {isScanning && <span className="animate-pulse inline-block ml-1">|</span>}
        </div>
      </div>

      <div className="mt-4 flex justify-between items-center font-sans">
        <div className="text-xs text-gray-500">Confidence Score</div>
        <div className={`text-sm font-bold ${confidence > 0.9 ? 'text-green-600' : 'text-yellow-600'}`}>
          {(confidence * 100).toFixed(1)}%
        </div>
      </div>
    </div>
  );
};
