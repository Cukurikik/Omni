//=============================================================================
// OMNI INTERFACE LAYER — MLOPS DASHBOARD (TYPESCRIPT / REACT)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: UI for monitoring RAG pipelines, Swarms agents, and ML metrics.
//=============================================================================

import React, { useState, useEffect } from 'react';
import { NetworkClient } from '@omni-bridge/network';

interface SystemMetrics {
    cpuUsage: number;
    gpuUsage: number;
    activeAgents: number;
    ragQueryCount: number;
}

/**
 * @html_template("mlops-dashboard")
 */
export const MLOpsDashboard: React.FC = () => {
    const [metrics, setMetrics] = useState<SystemMetrics | null>(null);

    useEffect(() => {
        // OMNI IDIOM: Event Loop subscription for real-time updates
        const sub = NetworkClient.subscribeToEvent('system.metrics.update', (data: SystemMetrics) => {
            setMetrics(data);
        });

        return () => sub.unsubscribe();
    }, []);

    if (!metrics) {
        return <div className="omni-loading">Initializing MLOps Telemetry...</div>;
    }

    return (
        <div className="omni-dashboard p-6 bg-gray-900 text-white min-h-screen">
            <h1 className="text-3xl font-bold mb-6 text-cyan-400">OMNI MLOps Nexus</h1>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <MetricCard title="CPU Core Utilization" value={`${metrics.cpuUsage.toFixed(1)}%`} color="text-green-400" />
                <MetricCard title="GPU VRAM Usage" value={`${metrics.gpuUsage.toFixed(1)}%`} color="text-purple-400" />
                <MetricCard title="Active Swarm Agents" value={metrics.activeAgents.toString()} color="text-yellow-400" />
                <MetricCard title="RAG Queries/sec" value={metrics.ragQueryCount.toString()} color="text-blue-400" />
            </div>
            
            <div className="mt-10">
                <h2 className="text-xl font-semibold mb-4">Active Pipelines</h2>
                <div className="bg-gray-800 p-4 rounded-lg shadow-lg">
                    {/* Placeholder for Pipeline component */}
                    <p className="text-gray-400">Monitoring Airflow-bridged execution trees...</p>
                </div>
            </div>
        </div>
    );
};

const MetricCard: React.FC<{title: string, value: string, color: string}> = ({title, value, color}) => (
    <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-md">
        <h3 className="text-gray-400 text-sm font-medium uppercase tracking-wide">{title}</h3>
        <p className={`text-4xl font-bold mt-2 ${color}`}>{value}</p>
    </div>
);
