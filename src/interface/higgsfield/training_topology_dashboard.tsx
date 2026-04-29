import React, { useEffect, useState } from 'react';

// OMNI Higgsfield - Training Topology Dashboard
// React/TSX component for monitoring distributed GPU nodes

interface NodeStatus {
    id: string;
    hostname: string;
    health: 'HEALTHY' | 'DEGRADED' | 'DEAD';
    gpu_utilization: number[]; // Array of % for each GPU
}

export const TopologyDashboard: React.FC = () => {
    const [nodes, setNodes] = useState<NodeStatus[]>([]);

    useEffect(() => {
        // Mock data representing the Fault Tolerance Monitor's output
        setNodes([
            { id: 'node_0', hostname: 'worker-us-east-1a', health: 'HEALTHY', gpu_utilization: [95, 98, 92, 99] },
            { id: 'node_1', hostname: 'worker-us-east-1b', health: 'HEALTHY', gpu_utilization: [94, 96, 91, 97] },
            { id: 'node_2', hostname: 'worker-us-east-1c', health: 'DEGRADED', gpu_utilization: [45, 0, 0, 0] },
        ]);
    }, []);

    return (
        <div className="p-6 bg-slate-900 min-h-screen text-slate-200">
            <h1 className="text-3xl font-bold text-fuchsia-400 mb-6">Higgsfield Cluster Topology</h1>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {nodes.map(node => (
                    <div key={node.id} className="bg-slate-800 p-5 rounded-xl border border-slate-700 shadow-lg">
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="text-xl font-bold">{node.hostname}</h3>
                            <span className={`px-3 py-1 rounded-full text-xs font-bold tracking-wider ${
                                node.health === 'HEALTHY' ? 'bg-emerald-900 text-emerald-300' :
                                node.health === 'DEGRADED' ? 'bg-amber-900 text-amber-300' :
                                'bg-rose-900 text-rose-300'
                            }`}>
                                {node.health}
                            </span>
                        </div>
                        <div className="space-y-3">
                            <p className="text-sm text-slate-400 mb-2">GPU Utilization</p>
                            {node.gpu_utilization.map((util, idx) => (
                                <div key={idx} className="flex items-center">
                                    <span className="w-16 text-xs text-slate-400">GPU {idx}</span>
                                    <div className="flex-1 h-3 bg-slate-900 rounded-full overflow-hidden">
                                        <div 
                                            className={`h-full ${util > 90 ? 'bg-fuchsia-500' : util > 50 ? 'bg-amber-500' : 'bg-slate-600'}`}
                                            style={{ width: `${util}%` }}
                                        />
                                    </div>
                                    <span className="w-12 text-right text-xs font-mono">{util}%</span>
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
