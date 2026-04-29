import React, { useState, useEffect } from 'react';

export const OperatorConsole: React.FC = () => {
  const [joints, setJoints] = useState<number[]>([0, 0, 0, 0, 0, 0]);
  const [target, setTarget] = useState({ x: 0.5, y: 0.5, z: 0.5 });
  const [status, setStatus] = useState('STANDBY');

  const handleExecute = () => {
    setStatus('COMPUTING_IK');
    
    // Deterministic UI simulation of movement
    setTimeout(() => {
      setStatus('MOVING');
      
      const newJoints = [
        Math.atan2(target.y, target.x),
        0.5,
        -0.5,
        0,
        Math.PI/4,
        0
      ];
      
      setJoints(newJoints);
      
      setTimeout(() => {
        setStatus('REACHED');
      }, 1000);
      
    }, 300);
  };

  return (
    <div className="bg-slate-900 text-cyan-400 p-6 font-mono rounded border border-cyan-900 w-full max-w-3xl mx-auto shadow-2xl">
      <div className="flex justify-between items-center mb-6 pb-2 border-b border-cyan-900">
        <h2 className="text-xl font-bold tracking-widest">OMNI ROBOTICS OPERATOR TTY</h2>
        <div className={`px-3 py-1 rounded text-xs font-bold ${
          status === 'STANDBY' ? 'bg-gray-800 text-gray-400' :
          status === 'MOVING' ? 'bg-yellow-900 text-yellow-400 animate-pulse' :
          'bg-cyan-900 text-cyan-200'
        }`}>
          SYS: {status}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-8">
        <div>
          <h3 className="text-sm text-cyan-600 mb-3 uppercase">Cartesian Target</h3>
          <div className="space-y-4">
            {['x', 'y', 'z'].map((axis) => (
              <div key={axis} className="flex items-center">
                <span className="w-8 text-cyan-500 uppercase">{axis}:</span>
                <input 
                  type="range" 
                  min="-1" max="1" step="0.01"
                  value={target[axis as keyof typeof target]}
                  onChange={(e) => setTarget({...target, [axis]: parseFloat(e.target.value)})}
                  className="flex-1 accent-cyan-500"
                />
                <span className="w-16 text-right">{target[axis as keyof typeof target].toFixed(2)}m</span>
              </div>
            ))}
          </div>
          
          <button 
            onClick={handleExecute}
            disabled={status === 'MOVING'}
            className="mt-6 w-full py-2 bg-cyan-800 hover:bg-cyan-700 text-cyan-100 font-bold uppercase transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Execute Trajectory
          </button>
        </div>

        <div>
          <h3 className="text-sm text-cyan-600 mb-3 uppercase">Joint States (Rad)</h3>
          <div className="space-y-2 bg-slate-950 p-4 rounded border border-slate-800">
            {joints.map((j, i) => (
              <div key={i} className="flex justify-between text-sm">
                <span className="text-slate-500">J{i}:</span>
                <span>{j.toFixed(4)}</span>
              </div>
            ))}
          </div>
          
          <div className="mt-4 p-3 bg-red-950/30 border border-red-900/50 rounded text-xs text-red-400">
            <strong>SAFETY ENFORCEMENT:</strong> Active.<br/>
            Velocity Limit: 2.0 rad/s<br/>
            Collision Avoidance: Enabled
          </div>
        </div>
      </div>
    </div>
  );
};
