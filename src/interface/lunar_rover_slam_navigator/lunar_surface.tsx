import React, { useState, useEffect } from 'react';

export const LunarSurface: React.FC = () => {
  const [roverX, setRoverX] = useState(20);
  const [scanRadius, setScanRadius] = useState(0);

  useEffect(() => {
    // Rover slowly drives forward
    const drive = setInterval(() => {
      setRoverX(prev => (prev + 0.5) % 100);
    }, 100);

    // SLAM LiDAR ping animation
    const ping = setInterval(() => {
      setScanRadius(0);
      const expand = setInterval(() => {
         setScanRadius(prev => {
            if (prev >= 40) { clearInterval(expand); return 40; }
            return prev + 5;
         });
      }, 50);
    }, 2000);

    return () => { clearInterval(drive); clearInterval(ping); };
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-gray-300">Lunar SLAM Nav</h2>
          <p className="text-xs text-slate-400">Visual-Inertial Odometry</p>
        </div>
        <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_#10b981] animate-pulse"></div>
      </div>

      <div className="bg-[#111] p-0 rounded border border-slate-800 mb-4 h-[200px] relative overflow-hidden flex flex-col justify-end">
         
         {/* Background Stars */}
         <div className="absolute inset-0 opacity-50">
            <div className="w-1 h-1 bg-white rounded-full absolute top-4 left-10"></div>
            <div className="w-1 h-1 bg-white rounded-full absolute top-12 left-32"></div>
            <div className="w-1 h-1 bg-white rounded-full absolute top-8 right-16"></div>
         </div>

         {/* Lunar Terrain (SVG) */}
         <svg viewBox="0 0 100 50" className="w-full h-1/2 absolute bottom-0 z-0 text-slate-600 fill-current">
            <path d="M0 50 L0 30 Q 15 25 25 35 T 50 20 T 75 40 T 100 25 L100 50 Z" opacity="0.3" />
            <path d="M0 50 L0 40 Q 20 30 30 45 T 60 30 T 90 45 T 100 35 L100 50 Z" opacity="0.5" />
            <path d="M0 50 L0 45 Q 25 35 40 48 T 70 40 T 100 48 L100 50 Z" />
         </svg>

         {/* Obstacles (Rocks/Craters) */}
         <div className="absolute bottom-4 left-[60%] w-6 h-3 bg-slate-800 rounded-t-full border border-slate-600 z-10"></div>
         
         {/* The Rover */}
         <div 
            className="absolute bottom-5 z-20 transition-all duration-75"
            style={{ left: `${roverX}%` }}
         >
            {/* Rover Body */}
            <div className="w-6 h-3 bg-amber-600 rounded-sm"></div>
            {/* Camera Mast */}
            <div className="w-1 h-4 bg-gray-400 absolute bottom-3 left-4"></div>
            {/* SLAM Scan Ring */}
            {scanRadius > 0 && scanRadius < 40 && (
               <div 
                  className="absolute bottom-0 left-3 transform -translate-x-1/2 rounded-full border border-emerald-500/50"
                  style={{ 
                     width: `${scanRadius * 2}px`, 
                     height: `${scanRadius * 2}px`,
                     opacity: 1 - (scanRadius / 40)
                  }}
               ></div>
            )}
         </div>

      </div>
      
      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Sensor: <span className="text-white">Star Tracker + IMU</span></span>
         <span>Filter: <span className="text-emerald-400">EKF Converged</span></span>
         <span className="col-span-2">Regolith Traction: <span className="text-white">Nominal (Slip 2%)</span></span>
      </div>
    </div>
  );
};
