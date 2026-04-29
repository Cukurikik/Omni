import React, { useState, useEffect } from 'react';

export const HUDOverlay: React.FC = () => {
  const [crosshairPos] = useState({ x: 50, y: 50 }); // Center screen (percentages)
  const [targetBox, setTargetBox] = useState<{x: number, y: number, w: number, h: number, lock: number} | null>(null);

  useEffect(() => {
    let t = 0;
    const interval = setInterval(() => {
      t++;
      
      // Deterministic simulation of target moving across screen and locking on
      const targetX = 30 + Math.abs(Math.sin(t * 0.05) * 40); // Sweeps 30% to 70%
      const targetY = 50 + Math.cos(t * 0.08) * 10;
      
      // Lock percentage mathematically based on distance to crosshair (50, 50)
      const dist = Math.sqrt(Math.pow(targetX - 50, 2) + Math.pow(targetY - 50, 2));
      const lockPct = Math.max(0, 100 - dist * 4);

      setTargetBox({
        x: targetX,
        y: targetY,
        w: 8, // 8% width
        h: 12, // 12% height
        lock: lockPct
      });

    }, 50);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-zinc-950 p-2 rounded border border-zinc-800 shadow-2xl max-w-3xl mx-auto font-mono text-emerald-400 relative overflow-hidden">
      
      <div className="absolute top-4 left-4 z-20 bg-zinc-900/80 px-2 py-1 rounded text-xs border border-emerald-500/30">
        CV_NET: YOLOv8 | STATUS: {targetBox && targetBox.lock > 80 ? 'LOCKED' : 'TRACKING'}
      </div>

      <div className="relative w-full aspect-video bg-zinc-900 border border-zinc-800 flex items-center justify-center">
        
        {/* Background Grid */}
        <div 
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage: 'linear-gradient(to right, #10b981 1px, transparent 1px), linear-gradient(to bottom, #10b981 1px, transparent 1px)',
            backgroundSize: '5% 5%'
          }}
        ></div>

        {/* Crosshair */}
        <div className="absolute z-30" style={{ left: `${crosshairPos.x}%`, top: `${crosshairPos.y}%` }}>
          <div className="absolute -left-4 -top-[1px] w-8 h-[2px] bg-emerald-500"></div>
          <div className="absolute -top-4 -left-[1px] h-8 w-[2px] bg-emerald-500"></div>
          <div className="w-1 h-1 bg-emerald-400 rounded-full shadow-[0_0_8px_#34d399] absolute -translate-x-1/2 -translate-y-1/2"></div>
        </div>

        {/* Target Box */}
        {targetBox && (
          <div 
            className={`absolute z-10 border-2 transition-colors duration-75 ${targetBox.lock > 80 ? 'border-red-500 bg-red-500/10' : 'border-amber-400 bg-amber-400/10'}`}
            style={{
              left: `${targetBox.x - targetBox.w/2}%`,
              top: `${targetBox.y - targetBox.h/2}%`,
              width: `${targetBox.w}%`,
              height: `${targetBox.h}%`
            }}
          >
            {/* Lock Line to Crosshair */}
            <svg className="absolute overflow-visible w-full h-full pointer-events-none" style={{ left: '50%', top: '50%' }}>
              <line 
                x1="0" 
                y1="0" 
                x2={`${(50 - targetBox.x) * 10}%`} 
                y2={`${(50 - targetBox.y) * 10}%`} 
                stroke={targetBox.lock > 80 ? '#ef4444' : '#fbbf24'} 
                strokeWidth="1" 
                opacity="0.5"
                strokeDasharray="4"
              />
            </svg>
            
            <div className="absolute -top-5 left-0 text-[10px] bg-zinc-900/80 px-1 rounded">
              L_{targetBox.lock.toFixed(0)}%
            </div>
          </div>
        )}
      </div>

    </div>
  );
};
