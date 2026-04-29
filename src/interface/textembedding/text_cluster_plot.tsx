import React, { useEffect, useState } from 'react';

// OMNI INTERFACE LAYER: Text Embedding
// Renders a 2D scatter plot of document embeddings reduced via PCA/t-SNE.

interface DataPoint {
  id: string;
  x: number;
  y: number;
  topic: string;
}

export const TextClusterPlot: React.FC = () => {
  const [points, setPoints] = useState<DataPoint[]>([]);

  useEffect(() => {
    const fetchEmbeddings = async () => {
      try {
        const res = await fetch('/api/omni/text/clusters');
        const json = await res.json();
        if (json.status === 'Ok') {
          setPoints(json.payload);
        }
      } catch (err) {
        console.error("OmniBridge Error:", err);
      }
    };
    
    fetchEmbeddings();
  }, []);

  const getTopicColor = (topic: string) => {
    const colors: Record<string, string> = {
      'finance': '#00ffcc',
      'sports': '#ff00cc',
      'technology': '#ffff00',
      'politics': '#ff4444'
    };
    return colors[topic] || '#ffffff';
  };

  return (
    <div className="p-8 bg-gray-900 text-white min-h-screen">
      <h1 className="text-3xl font-mono mb-6 text-fuchsia-400">Semantic Document Clusters</h1>
      
      <div className="relative w-full max-w-4xl h-[600px] border border-gray-700 bg-black rounded-lg overflow-hidden">
        {points.map((pt) => (
          <div 
            key={pt.id}
            className="absolute w-3 h-3 rounded-full cursor-pointer hover:scale-150 transition-transform opacity-80 shadow-[0_0_8px_rgba(255,255,255,0.5)]"
            style={{
              left: `${pt.x}%`,
              top: `${pt.y}%`,
              backgroundColor: getTopicColor(pt.topic),
              boxShadow: `0 0 10px ${getTopicColor(pt.topic)}`
            }}
            title={`Doc: ${pt.id} | Topic: ${pt.topic}`}
          />
        ))}
        {points.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center text-gray-500 font-mono animate-pulse">
            Projecting embeddings to 2D space...
          </div>
        )}
      </div>
      
      <div className="mt-6 flex gap-6 text-sm font-mono">
        <span className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-[#00ffcc]"></span> Finance</span>
        <span className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-[#ff00cc]"></span> Sports</span>
        <span className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-[#ffff00]"></span> Technology</span>
      </div>
    </div>
  );
};
