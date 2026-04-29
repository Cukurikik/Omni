import React, { useEffect, useRef } from 'react';

export const SimViewport: React.FC = () => {
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
      
      // Sky and Ground
      ctx.fillStyle = '#87CEEB'; // Sky blue
      ctx.fillRect(0, 0, canvas.width, canvas.height / 2);
      ctx.fillStyle = '#2f3e46'; // Road dark gray
      ctx.fillRect(0, canvas.height / 2, canvas.width, canvas.height / 2);

      // Road Lines (Perspective Fake)
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 4;
      ctx.setLineDash([20, 20]);
      ctx.beginPath();
      ctx.moveTo(canvas.width / 2, canvas.height / 2);
      ctx.lineTo(canvas.width / 2, canvas.height);
      // dash offset for motion
      ctx.lineDashOffset = -time * 50; 
      ctx.stroke();

      // Steering wheel UI Overlay
      const steeringAngle = Math.sin(time) * 0.5; // Radians
      ctx.save();
      ctx.translate(canvas.width / 2, canvas.height - 50);
      ctx.rotate(steeringAngle);
      ctx.strokeStyle = '#9ca3af';
      ctx.lineWidth = 10;
      ctx.setLineDash([]);
      ctx.beginPath();
      ctx.arc(0, 0, 40, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();

      // HUD overlay
      ctx.fillStyle = '#00ff00';
      ctx.font = '16px monospace';
      ctx.fillText(`FPS: ${(144 - Math.abs(Math.sin(time)*5)).toFixed(0)}`, 10, 20);
      ctx.fillText(`Speed: ${(60 + Math.sin(time * 0.5)*10).toFixed(1)} km/h`, 10, 40);

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => cancelAnimationFrame(animationFrameId);
  }, []);

  return (
    <div className="w-full flex flex-col items-center justify-center p-4 bg-gray-900 rounded-lg shadow-xl border border-gray-700">
      <h2 className="text-xl text-white font-mono mb-2">LGSVL Autonomy Simulator Viewport</h2>
      <canvas ref={canvasRef} width={640} height={360} className="rounded shadow-2xl border-2 border-black" />
    </div>
  );
};
