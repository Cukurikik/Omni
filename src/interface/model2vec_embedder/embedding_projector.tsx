import React, { useState, useEffect } from 'react';

interface Point3D {
  x: number;
  y: number;
  z: number;
  word: string;
}

export const EmbeddingProjector: React.FC = () => {
  const [points, setPoints] = useState<Point3D[]>([]);
  const [rotation, setRotation] = useState(0);

  useEffect(() => {
    // Deterministic embedding cluster generation
    const words = ["AI", "Model", "Vector", "Search", "Quantize", "Space", "Distance", "Query", "Graph", "Node"];
    const generatedPoints: Point3D[] = words.map((word, i) => ({
      x: Math.sin(i * 0.8) * 100,
      y: Math.cos(i * 1.2) * 100,
      z: Math.sin(i * 0.5) * 100,
      word
    }));
    setPoints(generatedPoints);

    const interval = setInterval(() => {
      setRotation(prev => (prev + 0.02) % (Math.PI * 2));
    }, 50);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-gray-900 text-gray-200 p-6 rounded-lg shadow-2xl max-w-2xl mx-auto border border-gray-700">
      <div className="mb-6 flex justify-between items-end border-b border-gray-700 pb-4">
        <div>
          <h2 className="text-2xl font-bold text-teal-400">Model2Vec Projector</h2>
          <p className="text-xs text-gray-500">PCA Reduced Int8 Static Embeddings</p>
        </div>
        <div className="text-xs bg-gray-800 px-3 py-1 rounded-full text-teal-300 border border-gray-700">
          DIM: 3 (Reduced from 384)
        </div>
      </div>

      <div className="relative h-80 bg-gray-950 rounded border border-gray-800 overflow-hidden flex items-center justify-center perspective-1000">
        <div className="absolute top-4 left-4 text-xs text-gray-600 font-mono">
          [Rot: {(rotation * (180 / Math.PI)).toFixed(1)}°]
        </div>

        {points.map((pt, i) => {
          // Deterministic 3D to 2D projection with rotation math
          const cosR = Math.cos(rotation);
          const sinR = Math.sin(rotation);
          
          const rx = pt.x * cosR - pt.z * sinR;
          const rz = pt.x * sinR + pt.z * cosR;
          
          const scale = 300 / (300 + rz);
          const px = rx * scale;
          const py = pt.y * scale;

          return (
            <div
              key={i}
              className="absolute flex flex-col items-center justify-center transform -translate-x-1/2 -translate-y-1/2 transition-all duration-75"
              style={{
                left: `calc(50% + ${px}px)`,
                top: `calc(50% + ${py}px)`,
                opacity: scale * 0.8,
                zIndex: Math.floor(scale * 100)
              }}
            >
              <div className="w-2 h-2 rounded-full bg-teal-400 shadow-[0_0_8px_#2dd4bf]"></div>
              <span className="text-xs mt-1 text-gray-400 font-mono select-none">{pt.word}</span>
            </div>
          );
        })}
      </div>

      <div className="mt-4 flex gap-4 text-xs text-gray-500 justify-center font-mono">
        <span>Dist: Cosine</span>
        <span>|</span>
        <span>Quant: Int8 ABS_MAX</span>
      </div>
    </div>
  );
};
