// OmniDashboardApp.tsx — Universal Dashboard Interface
// Layer: UI / TypeScript & React
//
// Real-time operations dashboard for monitoring OMNI Framework subsystems,
// including eBPF network latency, GPU VRAM offload status, and PPO rewards.

import React, { useEffect, useState } from 'react';

interface SystemStats {
  gpuVramUsage: number; // Percentage
  networkLatency: number; // ms
  activeInferences: number;
  tokensPerSecond: number;
}

export const OmniDashboardApp: React.FC = () => {
  const [stats, setStats] = useState<SystemStats>({
    gpuVramUsage: 0,
    networkLatency: 0,
    activeInferences: 0,
    tokensPerSecond: 0
  });

  const [connected, setConnected] = useState(false);

  useEffect(() => {
    // Connect to Elixir/Go SSE or WebSocket gateway
    const eventSource = new EventSource('http://127.0.0.1:8080/v1/metrics/stream');

    eventSource.onopen = () => setConnected(true);
    
    eventSource.onmessage = (event) => {
      const data: SystemStats = JSON.parse(event.data);
      setStats(data);
    };

    eventSource.onerror = () => {
      setConnected(false);
      eventSource.close();
    };

    return () => eventSource.close();
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8 font-sans">
      <header className="flex justify-between items-center mb-8 border-b border-gray-700 pb-4">
        <h1 className="text-3xl font-bold tracking-tight text-blue-400">
          OMNI Nexus Dashboard
        </h1>
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'} animate-pulse`}></div>
          <span className="text-sm font-medium text-gray-300">
            {connected ? 'Cluster Connected' : 'Disconnected'}
          </span>
        </div>
      </header>

      <main className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="GPU VRAM Usage" value={`${stats.gpuVramUsage.toFixed(1)}%`} color="text-purple-400" />
        <StatCard title="eBPF Network Latency" value={`${stats.networkLatency.toFixed(2)} ms`} color="text-yellow-400" />
        <StatCard title="Active Inferences" value={stats.activeInferences.toString()} color="text-green-400" />
        <StatCard title="Throughput (TPS)" value={`${stats.tokensPerSecond} tokens/s`} color="text-cyan-400" />
      </main>

      <section className="mt-12 bg-gray-800 p-6 rounded-lg border border-gray-700">
        <h2 className="text-xl font-semibold mb-4 text-gray-200">System Event Log</h2>
        <div className="h-64 overflow-y-auto font-mono text-sm text-gray-400 space-y-2">
           <p>[INFO] Tensor Offload Manager initialized.</p>
           <p>[INFO] Zig VRP Solver loaded via FFI.</p>
           <p>[INFO] Elixir Tri-LBM Supervisor pool started.</p>
           {/* In a real app, these map to a streaming array state */}
        </div>
      </section>
    </div>
  );
};

const StatCard: React.FC<{ title: string; value: string; color: string }> = ({ title, value, color }) => (
  <div className="bg-gray-800 p-6 rounded-lg border border-gray-700 shadow-lg">
    <h3 className="text-sm font-medium text-gray-400 mb-2 uppercase tracking-wider">{title}</h3>
    <p className={`text-4xl font-bold ${color}`}>{value}</p>
  </div>
);

export default OmniDashboardApp;
