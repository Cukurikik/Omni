import React, { useState, useEffect } from 'react';

// OMNI Monadic Type
export type MonadicResult<T, E> = { success: true; value: T } | { success: false; error: E };

export interface NodeStatus {
    nodeId: string;
    ipAddress: string;
    cpuUsage: number;
    memoryUsage: number;
    gpuUsage?: number;
    status: 'ALIVE' | 'DEAD' | 'DRAINING';
}

export const ClusterMonitor: React.FC = () => {
    const [nodes, setNodes] = useState<NodeStatus[]>([]);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchClusterState = async (): Promise<MonadicResult<NodeStatus[], string>> => {
            try {
                // In production, hits the OMNI Ray dashboard API wrapper
                const res = await fetch('/api/compute/ray/nodes');
                if (!res.ok) return { success: false, error: `HTTP ${res.status}` };
                const data = await res.json();
                return { success: true, value: data };
            } catch (err: any) {
                return { success: false, error: err.message };
            }
        };

        const interval = setInterval(() => {
            fetchClusterState().then(res => {
                if (res.success) {
                    setNodes(res.value);
                    setError(null);
                } else {
                    setError(res.error);
                    // Fallback mock strictly for layout review
                    setNodes([
                        { nodeId: 'node-0', ipAddress: '192.168.1.100', cpuUsage: 85, memoryUsage: 60, gpuUsage: 99, status: 'ALIVE' },
                        { nodeId: 'node-1', ipAddress: '192.168.1.101', cpuUsage: 42, memoryUsage: 30, status: 'ALIVE' }
                    ]);
                }
            });
        }, 2000);

        return () => clearInterval(interval);
    }, []);

    return (
        <div style={{ padding: '24px', backgroundColor: '#0d1117', color: '#c9d1d9', minHeight: '100vh', fontFamily: 'monospace' }}>
            <h1 style={{ color: '#58a6ff', borderBottom: '1px solid #30363d', paddingBottom: '10px' }}>
                OMNI Ray Cluster Monitor
            </h1>
            
            {error && <div style={{ backgroundColor: '#4a0f0f', color: '#ff7b72', padding: '10px', margin: '10px 0', border: '1px solid #ff7b72' }}>
                Connection Error: {error}
            </div>}

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px', marginTop: '20px' }}>
                {nodes.map(node => (
                    <div key={node.nodeId} style={{ backgroundColor: '#161b22', border: '1px solid #30363d', borderRadius: '6px', padding: '16px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #30363d', paddingBottom: '8px', marginBottom: '12px' }}>
                            <strong style={{ color: '#8b949e' }}>{node.ipAddress}</strong>
                            <span style={{ 
                                color: node.status === 'ALIVE' ? '#3fb950' : '#f85149',
                                fontWeight: 'bold'
                            }}>
                                {node.status}
                            </span>
                        </div>
                        
                        <div style={{ marginBottom: '8px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                <span>CPU</span>
                                <span>{node.cpuUsage}%</span>
                            </div>
                            <div style={{ width: '100%', height: '6px', backgroundColor: '#21262d', marginTop: '4px' }}>
                                <div style={{ width: `${node.cpuUsage}%`, height: '100%', backgroundColor: node.cpuUsage > 80 ? '#f85149' : '#3fb950' }} />
                            </div>
                        </div>

                        <div style={{ marginBottom: '8px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                <span>Memory</span>
                                <span>{node.memoryUsage}%</span>
                            </div>
                            <div style={{ width: '100%', height: '6px', backgroundColor: '#21262d', marginTop: '4px' }}>
                                <div style={{ width: `${node.memoryUsage}%`, height: '100%', backgroundColor: '#58a6ff' }} />
                            </div>
                        </div>

                        {node.gpuUsage !== undefined && (
                            <div style={{ marginBottom: '8px' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                    <span style={{ color: '#a371f7' }}>GPU Compute</span>
                                    <span style={{ color: '#a371f7' }}>{node.gpuUsage}%</span>
                                </div>
                                <div style={{ width: '100%', height: '6px', backgroundColor: '#21262d', marginTop: '4px' }}>
                                    <div style={{ width: `${node.gpuUsage}%`, height: '100%', backgroundColor: '#a371f7' }} />
                                </div>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};
