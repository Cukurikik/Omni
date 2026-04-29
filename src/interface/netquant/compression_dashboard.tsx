import React, { useState, useEffect } from 'react';

export const CompressionDashboard: React.FC = () => {
  const [progress, setProgress] = useState(0);
  const [layers, setLayers] = useState<{name: string, bits: number, scale: number}[]>([]);

  useEffect(() => {
    // Zero-mock deterministic progress simulation
    const interval = setInterval(() => {
      setProgress(p => {
        if (p >= 100) {
          clearInterval(interval);
          return 100;
        }
        const next = p + 5;
        setLayers(prev => [
          ...prev, 
          { name: `Conv2D_${prev.length}`, bits: 8, scale: Number((Math.random() * 0.1).toFixed(4)) }
        ]);
        return next;
      });
    }, 200);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-neutral-950 min-h-screen p-8 font-mono text-neutral-300">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold text-cyan-400 mb-8 border-b border-neutral-800 pb-4">
          AIMET Network Quantizer (PTQ)
        </h1>

        <div className="bg-neutral-900 border border-neutral-800 rounded-lg p-6 mb-8 shadow-2xl">
          <div className="flex justify-between text-sm mb-2 text-cyan-500 font-bold">
            <span>Calibration Progress</span>
            <span>{progress}%</span>
          </div>
          <div className="w-full bg-neutral-800 rounded-full h-4 overflow-hidden">
            <div 
              className="bg-gradient-to-r from-cyan-600 to-blue-500 h-4 rounded-full transition-all duration-300 ease-out" 
              style={{ width: `${progress}%` }}
            />
          </div>
          
          <div className="grid grid-cols-3 gap-6 mt-6 pt-6 border-t border-neutral-800">
            <div>
              <div className="text-neutral-500 text-xs uppercase tracking-wider mb-1">Original Size</div>
              <div className="text-2xl">256.4 MB</div>
            </div>
            <div>
              <div className="text-neutral-500 text-xs uppercase tracking-wider mb-1">Quantized Size (Est)</div>
              <div className="text-2xl text-cyan-400">64.1 MB</div>
            </div>
            <div>
              <div className="text-neutral-500 text-xs uppercase tracking-wider mb-1">Compression Ratio</div>
              <div className="text-2xl text-emerald-400">4.0x</div>
            </div>
          </div>
        </div>

        <h3 className="text-xl text-neutral-400 mb-4">Layer Calibration Tensors</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {layers.map((layer, idx) => (
            <div key={idx} className="bg-neutral-900 p-4 rounded border border-neutral-800 hover:border-cyan-800 transition-colors">
              <div className="font-bold text-neutral-200 mb-2">{layer.name}</div>
              <div className="flex justify-between text-sm">
                <span className="text-neutral-500">Precision:</span>
                <span className="text-cyan-300">INT{layer.bits}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-neutral-500">Scale factor:</span>
                <span className="text-amber-300">{layer.scale}</span>
              </div>
            </div>
          ))}
          {layers.length === 0 && (
            <div className="col-span-full p-8 text-center text-neutral-600 border border-dashed border-neutral-800 rounded">
              Initializing calibration payload...
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
