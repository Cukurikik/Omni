import React, { useState, useEffect } from 'react';

export const ArchitectureBuilder: React.FC = () => {
  const [layers, setLayers] = useState<{name: string, type: string}[]>([]);

  useEffect(() => {
    // Declarative construction sequence representing Ludwig AutoML
    const sequence = [
      { name: 'InputText', type: 'Input' },
      { name: 'WordEmbed', type: 'Encoder' },
      { name: 'ConcatCombiner', type: 'Combiner' },
      { name: 'Dense128', type: 'Decoder' },
      { name: 'OutputClass', type: 'Output' }
    ];

    let t = 0;
    const interval = setInterval(() => {
      if (t < sequence.length) {
        setLayers(prev => [...prev, sequence[t]]);
        t++;
      } else {
        clearInterval(interval);
      }
    }, 400);

    return () => clearInterval(interval);
  }, []);

  const getTypeColor = (type: string) => {
    switch(type) {
      case 'Input': return 'bg-blue-500';
      case 'Encoder': return 'bg-purple-500';
      case 'Combiner': return 'bg-yellow-500 text-black';
      case 'Decoder': return 'bg-pink-500';
      case 'Output': return 'bg-green-500';
      default: return 'bg-slate-500';
    }
  };

  return (
    <div className="bg-slate-50 p-6 rounded-lg border border-slate-200 shadow-xl max-w-sm mx-auto font-sans">
      <div className="mb-6 border-b border-slate-200 pb-2">
        <h2 className="text-xl font-bold text-slate-800">Ludwig Architecture</h2>
        <p className="text-xs text-slate-500">Declarative ECD Construction</p>
      </div>

      <div className="flex flex-col gap-3">
        {layers.map((layer, i) => (
          <div key={i} className="flex flex-col items-center">
            {i > 0 && <div className="w-px h-4 bg-slate-300 mb-3"></div>}
            <div className={`w-full py-3 px-4 rounded font-bold text-sm text-center shadow-sm text-white transition-all duration-300 animate-fade-in-up ${getTypeColor(layer.type)}`}>
              <div className="text-[10px] opacity-75 uppercase tracking-wider mb-1">{layer.type}</div>
              {layer.name}
            </div>
          </div>
        ))}
        {layers.length === 0 && (
          <div className="text-center text-slate-400 text-sm py-4">Compiling configuration...</div>
        )}
      </div>
    </div>
  );
};
