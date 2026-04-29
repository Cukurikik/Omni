import React, { useState, useEffect } from 'react';

export const BlochSphereViz: React.FC = () => {
  const [theta, setTheta] = useState(0); // Polar angle
  const [phi, setPhi] = useState(0);   // Azimuthal angle

  useEffect(() => {
    // Simulate applying Hadamard followed by continuous Z-rotation
    setTheta(Math.PI / 2); // Superposition (equator)
    
    const interval = setInterval(() => {
      setPhi(prev => (prev + 0.1) % (2 * Math.PI));
    }, 50);

    return () => clearInterval(interval);
  }, []);

  // Calculate 2D projection of 3D vector on Bloch sphere
  const radius = 50;
  const cx = 150;
  const cy = 80;
  
  // Isometric projection
  const x = cx + radius * Math.sin(theta) * Math.cos(phi);
  const y = cy - radius * Math.cos(theta) + radius * 0.3 * Math.sin(theta) * Math.sin(phi);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-blue-400">Quantum Simulator</h2>
        <p className="text-xs text-slate-400">Bloch Sphere State Vector</p>
      </div>

      <div className="relative h-48 bg-slate-950 p-2 rounded border border-slate-800 flex justify-center items-center">
        <svg width="100%" height="100%" viewBox="0 0 300 160">
          {/* Sphere Outline */}
          <circle cx={cx} cy={cy} r={radius} fill="none" stroke="#334155" strokeWidth="1" />
          
          {/* Equator */}
          <ellipse cx={cx} cy={cy} rx={radius} ry={radius * 0.3} fill="none" stroke="#334155" strokeWidth="1" strokeDasharray="2 2" />
          
          {/* Z-Axis */}
          <line x1={cx} y1={cy - radius} x2={cx} y2={cy + radius} stroke="#475569" strokeWidth="1" />
          
          {/* State Vector */}
          <line x1={cx} y1={cy} x2={x} y2={y} stroke="#60a5fa" strokeWidth="2" markerEnd="url(#arrow)" />
          
          <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#60a5fa" />
            </marker>
          </defs>
          
          {/* Basis Labels */}
          <text x={cx - 8} y={cy - radius - 5} fill="#94a3b8" fontSize="10">|0⟩</text>
          <text x={cx - 8} y={cy + radius + 12} fill="#94a3b8" fontSize="10">|1⟩</text>
        </svg>
      </div>
      <div className="mt-2 text-[10px] text-slate-500 font-mono flex justify-between">
         <span>Gate: Hadamard + Rz</span>
         <span>Fidelity: 99.98%</span>
      </div>
    </div>
  );
};
