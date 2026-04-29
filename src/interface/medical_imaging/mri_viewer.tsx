import React, { useEffect, useRef } from 'react';

export const MRIViewer: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let time = 0;

    const render = () => {
      time += 0.05;
      
      // Simulate axial MRI slice using mathematical interference patterns
      const imageData = ctx.createImageData(canvas.width, canvas.height);
      const data = imageData.data;
      
      const cx = canvas.width / 2;
      const cy = canvas.height / 2;
      const sliceDepth = Math.sin(time) * 10;

      for (let y = 0; y < canvas.height; y++) {
        for (let x = 0; x < canvas.width; x++) {
          const dx = x - cx;
          const dy = y - cy;
          const dist = Math.sqrt(dx * dx + dy * dy);
          
          // Deterministic brain-like blob pattern
          let val = Math.sin(dist * 0.05 + sliceDepth) * 128 + 128;
          val += Math.sin(dx * 0.1) * Math.cos(dy * 0.1) * 50;
          
          // Skull outline constraint
          if (dist > 120) val = 0;
          else if (dist > 110) val = 255; // skull bone (bright in T1)

          const idx = (y * canvas.width + x) * 4;
          data[idx] = val;     // R
          data[idx+1] = val;   // G
          data[idx+2] = val;   // B
          data[idx+3] = 255;   // Alpha
        }
      }

      ctx.putImageData(imageData, 0, 0);

      // HUD Overlay
      ctx.fillStyle = '#00ff00';
      ctx.font = '12px monospace';
      ctx.fillText(`Z-Slice: ${sliceDepth.toFixed(2)}mm`, 10, 20);
      ctx.fillText(`Filter: T1-Weighted`, 10, 35);

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => cancelAnimationFrame(animationFrameId);
  }, []);

  return (
    <div className="w-full flex flex-col items-center p-6 bg-black rounded-lg shadow-2xl">
      <h2 className="text-xl text-gray-300 font-mono mb-4">TorchIO Augmented Volume Viewer</h2>
      <canvas ref={canvasRef} width={300} height={300} className="rounded border border-gray-700 shadow-inner" />
    </div>
  );
};
