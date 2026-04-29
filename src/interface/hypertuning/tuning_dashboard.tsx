import React, { useState, useEffect } from 'react';

// OMNI INTERFACE LAYER: Hyperparameter Tuning Dashboard
// Renders trials, scores, and tuning progress.

interface TrialRecord {
  id: string;
  score: number;
  params: Record<string, number>;
}

export const TuningDashboard: React.FC = () => {
  const [trials, setTrials] = useState<TrialRecord[]>([]);
  const [bestScore, setBestScore] = useState<number>(0);

  useEffect(() => {
    // Zero-Mock WebSocket/Polling to OMNI Backend
    const pollTrials = async () => {
      try {
        const res = await fetch('/api/omni/tuning/trials');
        const json = await res.json();
        if (json.status === 'Ok') {
          setTrials(json.payload.trials);
          setBestScore(json.payload.bestScore);
        }
      } catch (err) {
        console.error("OmniBridge Error", err);
      }
    };
    
    const interval = setInterval(pollTrials, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-8 bg-black text-gray-200 min-h-screen">
      <h1 className="text-3xl font-mono text-cyan-400 mb-6">Omni Distributed Tuner</h1>
      
      <div className="flex gap-8 mb-8">
        <div className="bg-gray-900 border border-cyan-900 p-6 rounded-xl flex-1 shadow-lg">
          <h2 className="text-xl text-gray-400">Total Trials</h2>
          <p className="text-4xl font-bold text-cyan-200">{trials.length}</p>
        </div>
        <div className="bg-gray-900 border border-green-900 p-6 rounded-xl flex-1 shadow-lg">
          <h2 className="text-xl text-gray-400">Best Objective Score</h2>
          <p className="text-4xl font-bold text-green-400">{bestScore.toFixed(4)}</p>
        </div>
      </div>

      <h2 className="text-2xl font-mono mb-4 text-cyan-500 border-b border-gray-800 pb-2">Recent Trials</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-left font-mono">
          <thead className="text-gray-500 bg-gray-900">
            <tr>
              <th className="p-3">Trial ID</th>
              <th className="p-3">Score</th>
              <th className="p-3">Hyperparameters</th>
            </tr>
          </thead>
          <tbody>
            {trials.slice(-10).reverse().map(t => (
              <tr key={t.id} className="border-b border-gray-800 hover:bg-gray-800 transition-colors">
                <td className="p-3 text-cyan-600">{t.id}</td>
                <td className={`p-3 font-bold ${t.score === bestScore ? 'text-green-400' : 'text-gray-300'}`}>
                  {t.score.toFixed(4)}
                </td>
                <td className="p-3 text-sm text-gray-400">{JSON.stringify(t.params)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
