import React, { useState, useEffect } from 'react';

// OMNI TypeScript Interface Layer: Kiln-AI Evaluation Dashboard
// Reactive monitoring UI for RLHF and Agent evaluation metrics.

interface EvalMetric {
  id: string;
  prompt: string;
  score: number;
  passed: boolean;
  timestamp: string;
}

export const EvaluationDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<EvalMetric[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    // Zero-mock data hydration simulating WebSocket stream from Kiln Agent
    const fetchMetrics = async () => {
      try {
        const response = await fetch('/api/omni/kiln/evaluations');
        if (response.ok) {
          const data = await response.json();
          setMetrics(data.results);
        }
      } catch (err) {
        console.error("Failed to fetch Kiln evaluation metrics:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchMetrics();
  }, []);

  if (loading) {
    return <div className="p-8 text-center text-white bg-slate-900">Loading Evaluation Matrices...</div>;
  }

  const passRate = metrics.length > 0 
    ? (metrics.filter(m => m.passed).length / metrics.length) * 100 
    : 0;

  return (
    <div className="p-6 bg-slate-950 min-h-screen font-sans text-slate-200">
      <header className="mb-8 border-b border-slate-800 pb-4">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-500 bg-clip-text text-transparent">
          Kiln-AI: System Evaluation Telemetry
        </h1>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-lg">
          <h3 className="text-sm text-slate-400 uppercase tracking-widest">Total Evaluations</h3>
          <p className="text-4xl font-light mt-2">{metrics.length}</p>
        </div>
        <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-lg">
          <h3 className="text-sm text-slate-400 uppercase tracking-widest">Global Pass Rate</h3>
          <p className={`text-4xl font-light mt-2 ${passRate > 80 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {passRate.toFixed(1)}%
          </p>
        </div>
      </div>

      <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden shadow-lg">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-950 text-slate-400 text-sm">
              <th className="p-4 font-medium">Evaluation ID</th>
              <th className="p-4 font-medium">Prompt Substring</th>
              <th className="p-4 font-medium">ROUGE-L Score</th>
              <th className="p-4 font-medium">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50">
            {metrics.map(metric => (
              <tr key={metric.id} className="hover:bg-slate-800/50 transition-colors">
                <td className="p-4 font-mono text-xs text-slate-500">{metric.id}</td>
                <td className="p-4 truncate max-w-xs">{metric.prompt}</td>
                <td className="p-4 font-mono text-cyan-400">{(metric.score).toFixed(4)}</td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded text-xs tracking-wider uppercase ${metric.passed ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                    {metric.passed ? 'Passed' : 'Failed'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
