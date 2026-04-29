import React, { useState, useEffect } from 'react';

export const BlochSphere: React.FC = () => {
  const [theta, setTheta] = useState(Math.PI / 4);
  const [phi, setPhi] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate quantum state rotation (Rz and Rx gates)
      setPhi(p => (p + 0.1) % (2 * Math.PI));
      setTheta(t => {
         const next = t + (Math.random() * 0.1 - 0.05);
         return Math.max(0, Math.min(Math.PI, next)); // Clamp to 0..Pi
      });
    }, 50);
    return () => clearInterval(interval);
  }, []);

  // Calculate 2D projection of 3D Bloch vector
  const radius = 60;
  const cx = 100;
  const cy = 100;
  
  const x = radius * Math.sin(theta) * Math.cos(phi);
  const z = radius * Math.cos(theta); // Map Z to Y-axis on screen
  
  // Fake 3D depth by adjusting dot size based on Y-axis (depth)
  const y = radius * Math.sin(theta) * Math.sin(phi);
  const dotSize = 4 + (y / radius) * 2;

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-fuchsia-400">Quantum Sim</h2>
          <p className="text-xs text-slate-400">Qubit Bloch Sphere</p>
        </div>
        <div className="px-2 py-1 bg-slate-800 text-fuchsia-400 text-[10px] font-mono rounded border border-fuchsia-900/50">
          Superposition
        </div>
      </div>

      <div className="bg-slate-950 rounded border border-slate-800 h-[220px] relative flex items-center justify-center mb-4">
         
         <svg width="200" height="200" className="absolute">
            {/* Sphere outline */}
            <circle cx="100" cy="100" r={radius} fill="none" stroke="#334155" strokeWidth="1" />
            
            {/* Equator (dashed oval to look 3D) */}
            <ellipse cx="100" cy="100" rx={radius} ry={radius * 0.3} fill="none" stroke="#475569" strokeWidth="1" strokeDasharray="4 4" />
            
            {/* Z-Axis (|0> and |1>) */}
            <line x1="100" y1={100 - radius - 10} x2="100" y2={100 + radius + 10} stroke="#475569" strokeWidth="1" />
            <text x="96" y={100 - radius - 15} fill="#94a3b8" fontSize="10" fontFamily="monospace">|0⟩</text>
            <text x="96" y={100 + radius + 22} fill="#94a3b8" fontSize="10" fontFamily="monospace">|1⟩</text>
            
            {/* X-Axis */}
            <line x1={100 - radius - 10} y1="100" x2={100 + radius + 10} y2="100" stroke="#475569" strokeWidth="1" />
            
            {/* State Vector */}
            <line x1="100" y1="100" x2={cx + x} y2={cy - z} stroke="#e879f9" strokeWidth="2" />
            
            {/* Origin Dot */}
            <circle cx="100" cy="100" r="2" fill="#94a3b8" />
         </svg>
         
         {/* State Vector Head */}
         <div 
           className="absolute bg-fuchsia-400 rounded-full shadow-[0_0_10px_#e879f9]"
           style={{ 
              left: `${cx + x - dotSize/2}px`, 
              top: `${cy - z - dotSize/2}px`, 
              width: `${dotSize}px`, 
              height: `${dotSize}px` 
           }}
         ></div>
      </div>
      
      <div className="flex justify-between text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>θ: {(theta * (180/Math.PI)).toFixed(1)}°</span>
         <span>φ: {(phi * (180/Math.PI)).toFixed(1)}°</span>
         <span>Energy: <span className="text-emerald-400">-1.42eV</span></span>
      </div>
    </div>
  );
};
