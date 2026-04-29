import React, { useState, useEffect } from 'react';

export const AgentViewer: React.FC = () => {
  const [agentPos, setAgentPos] = useState(10);
  const goalPos = 90;
  const [reward, setReward] = useState(0);

  useEffect(() => {
    let currentPos = 10;
    const interval = setInterval(() => {
      // Deterministic policy simulation (move right towards goal)
      if (currentPos < goalPos) {
        currentPos += 2;
        setAgentPos(currentPos);
        setReward(prev => prev + 1); // Reward shaping logic mock
      } else {
        clearInterval(interval);
      }
    }, 100);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-gray-900 p-8 rounded-xl shadow-2xl max-w-3xl mx-auto border border-gray-700 text-white font-sans">
      <div className="flex justify-between items-center mb-8 border-b border-gray-700 pb-4">
        <h2 className="text-2xl font-bold tracking-wider text-green-400">RL Environment</h2>
        <div className="text-sm bg-gray-800 px-4 py-2 rounded shadow-inner">
          Cumulative Reward: <span className="font-mono text-yellow-400">{reward}</span>
        </div>
      </div>

      <div className="relative w-full h-12 bg-gray-800 rounded-full shadow-inner border border-gray-600 overflow-hidden">
        {/* Environment Track */}
        
        {/* Goal Indicator */}
        <div 
          className="absolute top-0 h-full w-8 bg-blue-500 opacity-50 flex items-center justify-center text-xs"
          style={{ left: `${goalPos}%` }}
        >
          GOAL
        </div>

        {/* Agent Actor */}
        <div 
          className="absolute top-1 w-10 h-10 bg-green-500 rounded-full shadow-[0_0_15px_rgba(34,197,94,0.6)] flex items-center justify-center font-bold text-gray-900 transition-all duration-100 ease-linear"
          style={{ left: `calc(${agentPos}% - 1.25rem)` }}
        >
          🤖
        </div>
      </div>
      
      <div className="mt-6 flex justify-between text-xs text-gray-400">
        <span>Start (0.0)</span>
        <span>Goal (10.0)</span>
      </div>
    </div>
  );
};
