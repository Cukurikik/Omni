import React, { useEffect, useState } from 'react';

export const CameraFeed: React.FC = () => {
  const [fps, setFps] = useState(0);
  const [detections, setDetections] = useState<{x: number, y: number, w: number, h: number, class: string}[]>([]);

  useEffect(() => {
    let frameCount = 0;
    let lastTime = performance.now();

    const interval = setInterval(() => {
      // Deterministic pseudo-random generation of bounding boxes
      const numDetections = Math.floor((performance.now() % 3) + 1);
      const newDetections = Array.from({length: numDetections}).map((_, i) => ({
        x: Math.abs(Math.sin(performance.now() / 1000 + i)) * 60,
        y: Math.abs(Math.cos(performance.now() / 800 + i)) * 60,
        w: 10 + (i * 5),
        h: 15 + (i * 5),
        class: i === 0 ? 'PERSON' : 'VEHICLE'
      }));

      setDetections(newDetections);
      frameCount++;

      const now = performance.now();
      if (now - lastTime >= 1000) {
        setFps(frameCount);
        frameCount = 0;
        lastTime = now;
      }
    }, 1000 / 30); // 30 FPS simulation

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-4 bg-gray-900 rounded border border-gray-700 max-w-lg mx-auto font-mono text-sm">
      <div className="flex justify-between text-green-400 mb-2 border-b border-gray-700 pb-1">
        <span>Omni Edge Inference (Roboflow Core)</span>
        <span>{fps} FPS | NPU: ACTIVE</span>
      </div>
      
      <div className="relative w-full aspect-video bg-black rounded overflow-hidden border border-gray-800">
        {/* Simulated Camera Feed Noise Background */}
        <div className="absolute inset-0 opacity-20 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-gray-700 via-gray-900 to-black"></div>
        
        {/* Bounding Boxes */}
        {detections.map((d, i) => (
          <div 
            key={i}
            className="absolute border-2 border-green-500 bg-green-500/20"
            style={{
              left: `${d.x}%`,
              top: `${d.y}%`,
              width: `${d.w}%`,
              height: `${d.h}%`,
              transition: 'all 0.1s linear'
            }}
          >
            <div className="bg-green-500 text-black text-[10px] font-bold px-1 absolute -top-4 left-0 whitespace-nowrap">
              {d.class} 0.9{i}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
