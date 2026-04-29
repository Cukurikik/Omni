import React, { useState, useEffect } from 'react';

export const ModelTopology: React.FC = () => {
  const [layers, setLayers] = useState<{id: number, type: string, load: number}[]>([]);

  useEffect(() => {
    // MobileViT Block Structure
    const structure = [
      { id: 1, type: 'Conv 3x3' },
      { id: 2, type: 'MV2 Block' },
      { id: 3, type: 'MV2 Block' },
      { id: 4, type: 'MobileViT Block 1' },
      { id: 5, type: 'MobileViT Block 2' },
      { id: 6, type: 'MobileViT Block 3' },
      { id: 7, type: 'Conv 1x1' },
      { id: 8, type: 'Linear (Classifier)' }
    ];

    let t = 0;
    const interval = setInterval(() => {
      t++;
      
      // Simulate inference load passing through the network deterministically
      const activeIdx = t % (structure.length + 5); 
      
      setLayers(structure.map((l, i) => {
        // Load spikes when activeIdx is nearby
        const distance = Math.abs(i - activeIdx);
        let load = 0;
        if (distance === 0) load = 100;
        else if (distance === 1) load = 40;
        else if (distance === 2) load = 10;
        
        return { ...l, load };
      }));

    }, 200);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded border border-slate-700 shadow-2xl max-w-md mx-auto font-sans">
      <div className="mb-6 border-b border-slate-800 pb-4">
        <h2 className="text-xl font-bold text-indigo-400">CV Network</h2>
        <p className="text-xs text-slate-500">MobileViT Topology Execution</p>
      </div>

      <div className="space-y-2">
        {layers.map(layer => (
          <div key={layer.id} className="relative flex items-center bg-slate-950 p-3 rounded border border-slate-800 overflow-hidden">
            
            {/* Load bar background */}
            <div 
              className="absolute left-0 top-0 bottom-0 bg-indigo-900/40 transition-all duration-200"
              style={{ width: `${layer.load}%` }}
            ></div>

            <div className="relative z-10 flex w-full justify-between items-center">
              <span className="text-sm font-mono text-slate-300">
                <span className="text-indigo-500 mr-2">[{layer.id}]</span>
                {layer.type}
              </span>
              
              <div className="text-xs font-mono text-slate-500">
                {layer.load > 0 ? (
                  <span className="text-indigo-300 animate-pulse">ACTV</span>
                ) : (
                  <span>IDLE</span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 pt-4 border-t border-slate-800">
        <div className="text-xs text-slate-500 flex justify-between">
          <span>Batch Size: 32</span>
          <span>Precision: FP16 Tensor</span>
        </div>
      </div>
    </div>
  );
};
