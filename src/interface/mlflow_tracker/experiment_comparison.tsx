import React, { useState, useEffect } from 'react';

export const ExperimentComparison: React.FC = () => {
  const [runs, setRuns] = useState<{id: string, loss: number, val_loss: number, duration: number}[]>([]);

  useEffect(() => {
    // Deterministic MLFlow Run Population
    const initialRuns = [
      { id: 'run-alpha', loss: 0.45, val_loss: 0.52, duration: 120 },
      { id: 'run-beta', loss: 0.38, val_loss: 0.45, duration: 145 },
      { id: 'run-gamma', loss: 0.30, val_loss: 0.41, duration: 210 }
    ];
    
    setRuns(initialRuns);

    let t = 0;
    const interval = setInterval(() => {
      t++;
      if (t % 5 === 0 && runs.length < 6) {
        setRuns(prev => [
          ...prev,
          { 
            id: `run-delta-${t}`, 
            loss: 0.28 - (t * 0.01), 
            val_loss: 0.39 - (t * 0.005), 
            duration: 200 + (t * 10) 
          }
        ]);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [runs.length]);

  return (
    <div className="bg-slate-50 p-6 rounded shadow border border-slate-200 max-w-2xl mx-auto font-sans">
      <div className="mb-6 border-b border-slate-200 pb-2">
        <h2 className="text-xl font-bold text-sky-600">MLFlow Experiment Tracking</h2>
        <p className="text-xs text-slate-500">Run Comparison View</p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-100 text-slate-600">
            <tr>
              <th className="p-3 font-bold">Run ID</th>
              <th className="p-3 font-bold">Training Loss</th>
              <th className="p-3 font-bold">Validation Loss</th>
              <th className="p-3 font-bold">Duration (s)</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((run, i) => (
              <tr key={i} className="border-b border-slate-100 hover:bg-slate-50 transition-colors">
                <td className="p-3 font-mono text-xs text-sky-700 font-bold">{run.id}</td>
                <td className="p-3">
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-2 bg-slate-200 rounded overflow-hidden">
                      <div className="h-full bg-rose-400" style={{width: `${run.loss * 100}%`}}></div>
                    </div>
                    <span>{run.loss.toFixed(3)}</span>
                  </div>
                </td>
                <td className="p-3">
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-2 bg-slate-200 rounded overflow-hidden">
                      <div className="h-full bg-amber-400" style={{width: `${run.val_loss * 100}%`}}></div>
                    </div>
                    <span>{run.val_loss.toFixed(3)}</span>
                  </div>
                </td>
                <td className="p-3 font-mono text-slate-600">{run.duration}s</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
