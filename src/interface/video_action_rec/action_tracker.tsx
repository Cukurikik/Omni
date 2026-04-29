import React, { useState, useEffect } from 'react';

export const ActionTracker: React.FC = () => {
  const [frame, setFrame] = useState(0);
  const [action, setAction] = useState("Standing");
  const [confidence, setConfidence] = useState(0.6);

  useEffect(() => {
    let t = 0;
    const interval = setInterval(() => {
      t++;
      setFrame(t);

      // Deterministic action state machine simulation based on time
      const cycle = t % 150;
      if (cycle < 50) {
        setAction("Walking");
        setConfidence(0.85 + Math.sin(t) * 0.05);
      } else if (cycle < 100) {
        setAction("Running");
        setConfidence(0.92 + Math.cos(t) * 0.03);
      } else {
        setAction("Standing");
        setConfidence(0.75 + Math.sin(t * 0.5) * 0.1);
      }

    }, 33); // ~30 FPS

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-gray-100 p-6 rounded-lg shadow border border-gray-300 font-sans max-w-2xl mx-auto">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-800">Action Recognition Stream</h2>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
          <span className="text-xs font-bold text-red-600 uppercase tracking-widest">Live</span>
        </div>
      </div>

      <div className="relative w-full h-64 bg-gray-900 rounded-lg border-2 border-gray-400 overflow-hidden mb-4 flex items-center justify-center">
        {/* Simulated Camera Feed / Optical Flow visualization */}
        <div 
          className="absolute inset-0 opacity-30"
          style={{
            background: `repeating-linear-gradient(${frame % 360}deg, transparent, transparent 10px, #3b82f6 10px, #3b82f6 20px)`
          }}
        />
        
        {/* Action Bounding Box Overlay */}
        <div 
          className="absolute border-2 border-green-400 shadow-[0_0_10px_#4ade80] transition-all duration-300"
          style={{
            width: action === 'Running' ? '120px' : '100px',
            height: action === 'Standing' ? '200px' : '160px',
            left: '50%',
            top: '50%',
            transform: `translate(-50%, -50%) skewX(${action === 'Running' ? -10 : 0}deg)`
          }}
        >
          <div className="absolute -top-6 left-0 bg-green-400 text-gray-900 text-xs font-bold px-2 py-0.5 whitespace-nowrap">
            {action} {(confidence * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white p-3 rounded border text-center">
          <div className="text-xs text-gray-500 uppercase">Frame</div>
          <div className="text-lg font-mono font-bold">{frame}</div>
        </div>
        <div className="bg-white p-3 rounded border text-center">
          <div className="text-xs text-gray-500 uppercase">Action</div>
          <div className="text-lg font-bold text-blue-600">{action}</div>
        </div>
        <div className="bg-white p-3 rounded border text-center">
          <div className="text-xs text-gray-500 uppercase">Confidence</div>
          <div className="text-lg font-mono font-bold text-green-600">{(confidence).toFixed(3)}</div>
        </div>
      </div>
    </div>
  );
};
