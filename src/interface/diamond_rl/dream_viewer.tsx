import React, { useState, useEffect } from 'react';

export const DreamViewer: React.FC = () => {
  const [agentPos, setAgentPos] = useState({ x: 50, y: 50 });
  const [diffusionStep, setDiffusionStep] = useState(100);
  const [reward, setReward] = useState(0);

  useEffect(() => {
    let t = 0;
    const interval = setInterval(() => {
      t++;
      
      // Deterministic environment navigation simulation
      // Circular trajectory with noise
      const targetX = 50 + Math.cos(t * 0.1) * 30;
      const targetY = 50 + Math.sin(t * 0.1) * 30;
      
      setAgentPos({ x: targetX, y: targetY });
      
      // Diffusion denoising process representation (100 -> 0)
      setDiffusionStep(prev => (prev > 0 ? prev - 2 : 100));
      
      // Deterministic reward
      setReward(Math.abs(Math.sin(t * 0.05)) * 10);
      
    }, 100);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-xl border border-slate-700 shadow-2xl max-w-lg mx-auto font-sans text-slate-200">
      <div className="flex justify-between items-end mb-6 border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-2xl font-bold text-violet-400">DIAMOND</h2>
          <p className="text-xs text-slate-500">World Model Dream Environment</p>
        </div>
        <div className="text-xs font-mono text-slate-400 bg-slate-800 px-2 py-1 rounded">
          T: {diffusionStep.toString().padStart(3, '0')}
        </div>
      </div>

      <div className="relative w-full aspect-square bg-slate-950 rounded-lg border border-slate-800 overflow-hidden mb-6">
        {/* Environment Grid */}
        <div 
          className="absolute inset-0 opacity-20"
          style={{
            backgroundImage: 'linear-gradient(to right, #334155 1px, transparent 1px), linear-gradient(to bottom, #334155 1px, transparent 1px)',
            backgroundSize: '10% 10%'
          }}
        ></div>

        {/* Diffusion Noise Overlay (Fades as t -> 0) */}
        <div 
          className="absolute inset-0 bg-slate-400 mix-blend-overlay transition-opacity duration-100"
          style={{ opacity: diffusionStep / 100 }}
        ></div>

        {/* Agent */}
        <div 
          className="absolute w-4 h-4 bg-violet-500 rounded-full shadow-[0_0_12px_#8b5cf6] transform -translate-x-1/2 -translate-y-1/2 transition-all duration-100"
          style={{ left: `${agentPos.x}%`, top: `${agentPos.y}%` }}
        >
          {/* Agent view frustum */}
          <div className="w-12 h-12 border-t-2 border-violet-400/30 rounded-full absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2"></div>
        </div>

        {/* Goal Indicator */}
        <div className="absolute w-6 h-6 border-2 border-emerald-500 rounded transform -translate-x-1/2 -translate-y-1/2 left-[50%] top-[50%]"></div>
      </div>

      <div className="flex justify-between items-center bg-slate-800 p-3 rounded">
        <div className="flex flex-col">
          <span className="text-xs text-slate-500 uppercase">Current Reward</span>
          <span className="text-lg font-mono text-emerald-400">+{reward.toFixed(2)}</span>
        </div>
        <div className="flex flex-col text-right">
          <span className="text-xs text-slate-500 uppercase">State</span>
          <span className="text-sm font-mono text-slate-300">
            [{agentPos.x.toFixed(1)}, {agentPos.y.toFixed(1)}]
          </span>
        </div>
      </div>
    </div>
  );
};
