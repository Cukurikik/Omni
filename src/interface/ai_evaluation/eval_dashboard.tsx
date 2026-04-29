import React, { useState } from 'react';

interface Metric {
  name: string;
  value: number;
  status: 'STABLE' | 'DEGRADED';
}

export const EvalDashboard: React.FC = () => {
  const [metrics] = useState<Metric[]>([
    { name: 'Accuracy', value: 0.94, status: 'STABLE' },
    { name: 'Data Drift', value: 0.65, status: 'DEGRADED' },
    { name: 'Latency (ms)', value: 45, status: 'STABLE' }
  ]);

  return (
    <div className="w-full max-w-4xl mx-auto p-6 bg-gray-50 font-sans">
      <h2 className="text-2xl font-bold text-gray-800 mb-6 border-b pb-2">UpTrain Evaluation Matrix</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {metrics.map((m, idx) => (
          <div key={idx} className="bg-white p-6 rounded-lg shadow border border-gray-100 flex flex-col items-center justify-center">
            <span className="text-gray-500 text-sm font-medium uppercase tracking-wider mb-2">{m.name}</span>
            <span className="text-4xl font-bold text-gray-900 mb-4">{m.value}</span>
            <span className={`px-3 py-1 rounded-full text-xs font-bold ${
              m.status === 'STABLE' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {m.status}
            </span>
          </div>
        ))}
      </div>
      
      <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded text-sm text-blue-800">
        <p><strong>System Note:</strong> Data drift detected in recent embedding projections. Recommend reviewing Quality Gate logs.</p>
      </div>
    </div>
  );
};
