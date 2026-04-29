import React, { useState, useEffect } from 'react';

export const PointCloudRender: React.FC = () => {
  const [points, setPoints] = useState<{x:number, y:number, z:number, i:number}[]>([]);
  const [rotation, setRotation] = useState(0);

  useEffect(() => {
    // Generate a mock static point cloud (simulating a hallway/tunnel)
    const initialCloud = [];
    for(let i=0; i<150; i++) {
       // Walls
       initialCloud.push({ x: 30 + Math.random()*5, y: -40 + Math.random()*80, z: Math.random()*20, i: Math.random() });
       initialCloud.push({ x: -30 - Math.random()*5, y: -40 + Math.random()*80, z: Math.random()*20, i: Math.random() });
       // Floor
       initialCloud.push({ x: -30 + Math.random()*60, y: -40 + Math.random()*80, z: 0 + Math.random()*2, i: Math.random() * 0.3 });
    }
    setPoints(initialCloud);

    const interval = setInterval(() => {
      // Rotate the point cloud view
      setRotation(prev => (prev + 0.05) % (Math.PI * 2));
    }, 50);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-teal-400">LiDAR SLAM</h2>
          <p className="text-xs text-slate-400">ICP Point Cloud Fusion</p>
        </div>
        <div className="text-[10px] font-mono bg-teal-900/30 text-teal-400 border border-teal-800 px-2 py-1 rounded">
          10 Hz
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 relative h-[220px] mb-4 overflow-hidden perspective-1000">
         
         <div className="absolute inset-0 flex items-center justify-center transform-gpu" style={{ transform: `rotateY(${rotation}rad) rotateX(15deg)` }}>
            {points.map((pt, idx) => {
               // Pseudo-3D projection
               const scale = 200 / (200 + pt.y);
               const px = pt.x * scale;
               const py = -pt.z * scale * 2; // Invert Z to screen Y
               
               // Intensity based color (LiDAR reflectivity)
               const color = pt.i > 0.7 ? '#facc15' : pt.i > 0.4 ? '#2dd4bf' : '#334155';
               
               return (
                 <div 
                   key={idx}
                   className="absolute w-1 h-1 rounded-full"
                   style={{
                      left: `calc(50% + ${px}px)`,
                      top: `calc(60% + ${py}px)`,
                      backgroundColor: color,
                      opacity: scale * 0.8
                   }}
                 ></div>
               );
            })}
         </div>

         {/* Ego Vehicle (Center) */}
         <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-4 h-6 border border-rose-500 bg-rose-900/50 rounded shadow-[0_0_10px_#f43f5e] z-10"></div>
      </div>
      
      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Points: 1.2M/s</span>
         <span>Voxel Size: <span className="text-emerald-400">5.0 cm</span></span>
         <span className="col-span-2">ICP Alignment RMSE: <span className="text-teal-400 font-bold">0.012 m</span></span>
      </div>
    </div>
  );
};
