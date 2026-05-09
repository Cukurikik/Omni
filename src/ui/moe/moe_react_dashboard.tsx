// moe_react_dashboard.tsx — Interface / UI
// Layer: Interface / Web — Real-Time MoE Telemetry Dashboard
//
// A React component that connects to the Ruby/Go backend APIs to render a live
// heatmap of the MoE cluster. It tracks expert utilization, VRAM usage, and 
// current token throughput using WebSockets or SSE.

import React, { useState, useEffect } from 'react';

// Mock types
interface ExpertMetrics {
  id: number;
  name: string;
  tps: number;
  vram_percent: number;
  status: 'active' | 'standby' | 'overloaded';
}

export const MoEDashboard: React.FC = () => {
  const [experts, setExperts] = useState<ExpertMetrics[]>([]);
  const [clusterTps, setClusterTps] = useState(0);

  useEffect(() => {
    // Connect to the Go Telemetry SSE stream
    const eventSource = new EventSource('/api/v1/telemetry/stream');

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setExperts(data.experts);
      setClusterTps(data.cluster_tps);
    };

    return () => eventSource.close();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-400 bg-green-900/20';
      case 'standby': return 'text-yellow-400 bg-yellow-900/20';
      case 'overloaded': return 'text-red-400 bg-red-900/20 animate-pulse';
      default: return 'text-gray-400 bg-gray-800';
    }
  };

  return (
    <div className="p-6 bg-gray-900 min-h-screen text-white font-mono">
      <header className="mb-8 border-b border-gray-700 pb-4">
        <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">
          OMNI MoE Cluster Telemetry
        </h1>
        <p className="text-gray-400 mt-2">Global Throughput: {clusterTps.toLocaleString()} Tokens/sec</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {experts.map(expert => (
          <div key={expert.id} className="bg-gray-800 border border-gray-700 rounded-lg p-4 shadow-lg hover:border-blue-500 transition-colors">
            <div className="flex justify-between items-center mb-2">
              <h2 className="text-xl font-semibold">Expert {expert.id}</h2>
              <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(expert.status)}`}>
                {expert.status.toUpperCase()}
              </span>
            </div>
            <p className="text-gray-400 text-sm mb-4">{expert.name}</p>
            
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Throughput:</span>
                <span className="font-bold">{expert.tps} tps</span>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>VRAM:</span>
                  <span>{expert.vram_percent}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-1.5">
                  <div 
                    className={`h-1.5 rounded-full ${expert.vram_percent > 90 ? 'bg-red-500' : 'bg-blue-500'}`} 
                    style={{ width: `${expert.vram_percent}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {experts.length === 0 && (
        <div className="flex justify-center items-center h-64 text-gray-500">
          Connecting to telemetry stream...
        </div>
      )}
    </div>
  );
};
