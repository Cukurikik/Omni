import React, { useEffect, useState } from 'react';

interface PerfMetric {
  id: string;
  gflops: number;
  memoryUsage: number;
}

export const PerfMonitor: React.FC = () => {
  const [metrics, setMetrics] = useState<PerfMetric[]>([]);

  useEffect(() => {
    let animationFrameId: number;
    let time = 0;

    const updateMetrics = () => {
      time += 0.1;
      
      const newMetrics: PerfMetric[] = Array.from({ length: 4 }).map((_, i) => {
        return {
          id: `HyperNode-${i}`,
          gflops: 150 + Math.sin(time + i) * 50,
          memoryUsage: 4000 + Math.cos(time * 0.5 + i) * 1000
        };
      });

      setMetrics(newMetrics);
      
      setTimeout(() => {
        animationFrameId = requestAnimationFrame(updateMetrics);
      }, 500); // Update every 500ms
    };

    updateMetrics();

    return () => cancelAnimationFrame(animationFrameId);
  }, []);

  return (
    <div className="w-full max-w-4xl mx-auto p-6 bg-gray-950 text-emerald-400 font-mono rounded shadow-2xl border border-gray-800">
      <h2 className="text-2xl font-bold mb-6 text-white border-b border-gray-800 pb-2">Hyperlearn Performance Matrix</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {metrics.map(m => (
          <div key={m.id} className="p-4 bg-gray-900 border border-emerald-900 rounded-lg">
            <h3 className="text-lg text-emerald-200 mb-2">{m.id}</h3>
            <div className="flex justify-between items-center mb-1">
              <span>Throughput:</span>
              <span className="font-bold text-white">{m.gflops.toFixed(1)} GFLOPS</span>
            </div>
            <div className="w-full bg-gray-800 h-2 rounded mb-3 overflow-hidden">
              <div className="bg-emerald-500 h-full" style={{ width: `${(m.gflops / 200) * 100}%` }}></div>
            </div>

            <div className="flex justify-between items-center mb-1">
              <span>Memory:</span>
              <span className="font-bold text-white">{(m.memoryUsage / 1024).toFixed(2)} GB</span>
            </div>
            <div className="w-full bg-gray-800 h-2 rounded overflow-hidden">
              <div className="bg-blue-500 h-full" style={{ width: `${(m.memoryUsage / 8192) * 100}%` }}></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
