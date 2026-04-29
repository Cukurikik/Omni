import React, { useState, useEffect } from 'react';

// OMNI RL: Training Monitor
// TypeScript React UI for visualizing Reinforcement Learning reward curves in real-time.
// Source: rlcode/reinforcement-learning

type EpisodeData = {
    episode: number;
    reward: number;
    loss: number;
};

export const RLTrainingMonitor: React.FC = () => {
    const [data, setData] = useState<EpisodeData[]>([]);
    const [isRunning, setIsRunning] = useState(false);

    useEffect(() => {
        let interval: NodeJS.Timeout;
        if (isRunning) {
            interval = setInterval(() => {
                setData(prev => {
                    const nextEp = prev.length + 1;
                    // Simulate logarithmic learning curve with noise
                    const baseReward = Math.min(100, Math.log10(nextEp) * 30);
                    const noise = (Math.random() - 0.5) * 10;
                    const simulatedReward = baseReward + noise;
                    
                    const loss = Math.max(0.1, 10.0 / Math.sqrt(nextEp)) + Math.random();

                    const newPoint = { episode: nextEp, reward: simulatedReward, loss };
                    
                    // Keep last 50 points
                    if (prev.length > 50) return [...prev.slice(1), newPoint];
                    return [...prev, newPoint];
                });
            }, 500);
        }
        return () => clearInterval(interval);
    }, [isRunning]);

    return (
        <div className="bg-gray-900 text-white p-6 rounded-xl font-mono shadow-2xl max-w-2xl mx-auto mt-10">
            <h2 className="text-2xl text-blue-400 font-bold mb-4">RL Training Monitor</h2>
            
            <div className="flex gap-4 mb-6">
                <button 
                    className={`px-4 py-2 rounded font-bold ${isRunning ? 'bg-red-500 hover:bg-red-600' : 'bg-green-500 hover:bg-green-600'}`}
                    onClick={() => setIsRunning(!isRunning)}
                >
                    {isRunning ? 'Stop Training' : 'Start Training'}
                </button>
                <button 
                    className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded"
                    onClick={() => setData([])}
                >
                    Reset Data
                </button>
            </div>

            <div className="space-y-4">
                <div className="bg-gray-800 p-4 rounded border border-gray-700">
                    <h3 className="text-sm text-gray-400 mb-2">Total Reward</h3>
                    <div className="flex items-end h-32 gap-1">
                        {data.map(d => (
                            <div 
                                key={d.episode}
                                className="bg-green-400 w-full"
                                style={{ height: `${Math.max(1, d.reward)}%` }}
                                title={`Ep ${d.episode}: ${d.reward.toFixed(2)}`}
                            />
                        ))}
                    </div>
                </div>

                <div className="bg-gray-800 p-4 rounded border border-gray-700">
                    <h3 className="text-sm text-gray-400 mb-2">MSE Loss</h3>
                    <div className="flex items-end h-32 gap-1">
                        {data.map(d => (
                            <div 
                                key={d.episode}
                                className="bg-red-400 w-full"
                                style={{ height: `${Math.min(100, d.loss * 10)}%` }}
                                title={`Ep ${d.episode}: ${d.loss.toFixed(4)}`}
                            />
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};
