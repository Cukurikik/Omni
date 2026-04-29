import React, { useState, useEffect } from 'react';

interface DataPoint {
  time: string;
  value: number;
  anomaly: boolean;
}

export const ForecastDashboard: React.FC = () => {
  const [data, setData] = useState<DataPoint[]>([]);

  useEffect(() => {
    let t = 0;
    const interval = setInterval(() => {
      t++;
      
      // Deterministic math logic
      const value = 100 + Math.sin(t * 0.5) * 20 + Math.cos(t * 0.1) * 10;
      const isAnomaly = value > 125 || value < 75; // Z-score threshold mock
      
      const point = {
        time: new Date(Date.now() + t * 1000).toLocaleTimeString(),
        value: Number(value.toFixed(2)),
        anomaly: isAnomaly
      };

      setData(prev => [...prev.slice(-19), point]);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200 max-w-2xl mx-auto font-sans">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-extrabold text-gray-800 tracking-tight">Time Series Forecast</h2>
        <span className="px-3 py-1 bg-blue-100 text-blue-800 text-xs font-bold rounded-full uppercase tracking-wide">
          Live Stream
        </span>
      </div>

      <div className="h-64 flex items-end space-x-2 border-b border-l border-gray-300 p-2 relative bg-gray-50 rounded-bl">
        {data.map((d, i) => (
          <div key={i} className="flex-1 flex flex-col items-center justify-end relative group">
            {d.anomaly && (
              <div className="absolute -top-6 text-red-500 font-bold text-xs animate-bounce">!</div>
            )}
            <div 
              className={`w-full transition-all duration-300 rounded-t-sm ${d.anomaly ? 'bg-red-500' : 'bg-blue-500'}`}
              style={{ height: `${Math.max(5, (d.value / 150) * 100)}%` }}
            ></div>
            
            {/* Tooltip */}
            <div className="hidden group-hover:block absolute bottom-full mb-2 bg-gray-800 text-white text-xs p-2 rounded shadow-lg z-10 whitespace-nowrap">
              {d.time}<br/>Val: {d.value}
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-6 flex gap-4 text-sm">
        <div className="flex items-center"><div className="w-3 h-3 bg-blue-500 rounded-sm mr-2"></div> Normal Pattern</div>
        <div className="flex items-center"><div className="w-3 h-3 bg-red-500 rounded-sm mr-2"></div> Detected Anomaly</div>
      </div>
    </div>
  );
};
