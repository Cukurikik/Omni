import React, { useState, useEffect } from 'react';

export const RoboticArmViz: React.FC = () => {
  const [q1, setQ1] = useState(Math.PI / 4);
  const [q2, setQ2] = useState(-Math.PI / 4);

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate trajectory execution
      setQ1(prev => prev + Math.sin(Date.now() / 1000) * 0.05);
      setQ2(prev => prev + Math.cos(Date.now() / 800) * 0.05);
    }, 50);
    return () => clearInterval(interval);
  }, []);

  // Forward Kinematics to calculate X/Y positions on screen
  const L1 = 60;
  const L2 = 50;
  
  const originX = 100;
  const originY = 150;

  const elbowX = originX + L1 * Math.cos(q1);
  const elbowY = originY - L1 * Math.sin(q1);

  const endEffectorX = elbowX + L2 * Math.cos(q1 + q2);
  const endEffectorY = elbowY - L2 * Math.sin(q1 + q2);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-sky-400">Kinematic Planner</h2>
          <p className="text-xs text-slate-400">OMNI 2-Axis Cobot</p>
        </div>
        <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_#10b981] animate-pulse"></div>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 relative h-[200px] mb-4 flex items-center justify-center">
         
         <svg width="200" height="200" className="absolute">
            {/* Target Area */}
            <circle cx="150" cy="50" r="10" fill="none" stroke="#ef4444" strokeWidth="1" strokeDasharray="2 2" />
            <line x1="145" y1="50" x2="155" y2="50" stroke="#ef4444" strokeWidth="1" />
            <line x1="150" y1="45" x2="150" y2="55" stroke="#ef4444" strokeWidth="1" />

            {/* Link 1 (Shoulder to Elbow) */}
            <line x1={originX} y1={originY} x2={elbowX} y2={elbowY} stroke="#38bdf8" strokeWidth="6" strokeLinecap="round" />
            
            {/* Link 2 (Elbow to End Effector) */}
            <line x1={elbowX} y1={elbowY} x2={endEffectorX} y2={endEffectorY} stroke="#0ea5e9" strokeWidth="4" strokeLinecap="round" />

            {/* Joints */}
            <circle cx={originX} cy={originY} r="6" fill="#0f172a" stroke="#cbd5e1" strokeWidth="2" /> {/* Shoulder */}
            <circle cx={elbowX} cy={elbowY} r="5" fill="#0f172a" stroke="#cbd5e1" strokeWidth="2" /> {/* Elbow */}
            
            {/* End Effector Tool */}
            <circle cx={endEffectorX} cy={endEffectorY} r="4" fill="#fbbf24" />
         </svg>
      </div>
      
      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Q1: {(q1 * (180/Math.PI)).toFixed(1)}°</span>
         <span>Q2: {(q2 * (180/Math.PI)).toFixed(1)}°</span>
         <span>TCP X: {(endEffectorX - originX).toFixed(1)}mm</span>
         <span>TCP Y: {(originY - endEffectorY).toFixed(1)}mm</span>
      </div>
    </div>
  );
};
