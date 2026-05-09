// moe_organics_dashboard.tsx — Interface / UI
// Layer: Interface / Web — MoE Environment Dashboard
//
// React components representing a monitoring dashboard for the MoE ecosystem.
// Tracks resource consumption, expert utilization, and organic cluster growth.

import React, { useState, useEffect } from 'react';

interface ExpertMetrics {
  id: number;
  loadPercentage: number;
  memoryUsedMB: number;
  status: 'Healthy' | 'Throttled' | 'Offline';
}

interface ClusterMetrics {
  totalExperts: number;
  activeRequests: number;
  averageLatencyMs: number;
  experts: ExpertMetrics[];
}

export const MoEOrganicsDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<ClusterMetrics | null>(null);

  useEffect(() => {
    // Mock fetching telemetry from the Go API Gateway
    const fetchTelemetry = () => {
      const mockExperts: ExpertMetrics[] = Array.from({ length: 8 }).map((_, i) => ({
        id: i,
        loadPercentage: Math.floor(Math.random() * 100),
        memoryUsedMB: 1024 + Math.floor(Math.random() * 2048),
        status: Math.random() > 0.1 ? 'Healthy' : 'Throttled'
      }));

      setMetrics({
        totalExperts: 8,
        activeRequests: Math.floor(Math.random() * 5000),
        averageLatencyMs: 45 + Math.floor(Math.random() * 15),
        experts: mockExperts
      });
    };

    fetchTelemetry();
    const interval = setInterval(fetchTelemetry, 2000);
    return () => clearInterval(interval);
  }, []);

  if (!metrics) return <div className="text-white">Loading MoE Telemetry...</div>;

  return (
    <div className="p-6 bg-gray-900 min-h-screen font-sans text-gray-100">
      <header className="mb-8 border-b border-gray-700 pb-4">
        <h1 className="text-3xl font-bold text-blue-400">OMNI MoE Cluster Dashboard</h1>
        <p className="text-sm text-gray-400 mt-2">Organic node monitoring and expert utilization metrics.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <MetricCard title="Active Requests" value={metrics.activeRequests.toLocaleString()} />
        <MetricCard title="Avg Latency" value={`${metrics.averageLatencyMs} ms`} />
        <MetricCard title="Total Experts" value={metrics.totalExperts.toString()} />
      </div>

      <h2 className="text-xl font-semibold mb-4">Expert Nodes Overview</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.experts.map(expert => (
          <ExpertCard key={expert.id} expert={expert} />
        ))}
      </div>
    </div>
  );
};

const MetricCard: React.FC<{ title: string; value: string }> = ({ title, value }) => (
  <div className="bg-gray-800 p-6 rounded-lg shadow-md border border-gray-700">
    <h3 className="text-gray-400 text-sm font-medium uppercase tracking-wider">{title}</h3>
    <div className="mt-2 text-3xl font-bold text-white">{value}</div>
  </div>
);

const ExpertCard: React.FC<{ expert: ExpertMetrics }> = ({ expert }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Healthy': return 'bg-green-500';
      case 'Throttled': return 'bg-yellow-500';
      case 'Offline': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
      <div className="flex justify-between items-center mb-3">
        <h4 className="font-semibold text-lg">Expert {expert.id}</h4>
        <span className={`px-2 py-1 text-xs font-bold rounded-full text-white ${getStatusColor(expert.status)}`}>
          {expert.status}
        </span>
      </div>
      
      <div className="mb-2">
        <div className="flex justify-between text-xs text-gray-400 mb-1">
          <span>Compute Load</span>
          <span>{expert.loadPercentage}%</span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2">
          <div 
            className="bg-blue-500 h-2 rounded-full transition-all duration-500" 
            style={{ width: `${expert.loadPercentage}%` }}
          />
        </div>
      </div>

      <div className="text-xs text-gray-400 mt-3">
        VRAM Used: <span className="text-gray-200">{expert.memoryUsedMB} MB</span>
      </div>
    </div>
  );
};
