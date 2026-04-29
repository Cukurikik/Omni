import React from 'react';

// OMNI MILVUS: Cluster Status Dashboard
// React UI to monitor Milvus Query Nodes, Data Nodes, and Index Nodes.
// Source: milvus-io/milvus

interface NodeStatus {
    id: string;
    type: 'Query' | 'Data' | 'Index';
    status: 'Healthy' | 'Syncing' | 'Offline';
    cpuUsage: number;
    ramUsageGb: number;
}

export const ClusterStatus: React.FC = () => {
    // Simulated state
    const nodes: NodeStatus[] = [
        { id: "qn-01", type: "Query", status: "Healthy", cpuUsage: 45, ramUsageGb: 16.2 },
        { id: "qn-02", type: "Query", status: "Healthy", cpuUsage: 50, ramUsageGb: 15.8 },
        { id: "dn-01", type: "Data", status: "Syncing", cpuUsage: 20, ramUsageGb: 32.1 },
        { id: "in-01", type: "Index", status: "Healthy", cpuUsage: 98, ramUsageGb: 64.0 }, // Indexing is CPU intensive
    ];

    const getStatusColor = (status: string) => {
        if (status === 'Healthy') return '#2ecc71';
        if (status === 'Syncing') return '#f1c40f';
        return '#e74c3c';
    };

    return (
        <div style={{ padding: '20px', fontFamily: 'sans-serif', background: '#121212', color: '#fff', minHeight: '100vh' }}>
            <h2 style={{ color: '#00a8ff' }}>Milvus Distributed Cluster Status</h2>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
                {nodes.map(node => (
                    <div key={node.id} style={{ border: '1px solid #333', borderRadius: '8px', padding: '15px', background: '#1e1e1e' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <h3 style={{ margin: 0 }}>{node.id}</h3>
                            <span style={{ padding: '3px 8px', borderRadius: '12px', fontSize: '12px', background: getStatusColor(node.status), color: '#000' }}>
                                {node.status}
                            </span>
                        </div>
                        <p style={{ color: '#aaa', margin: '5px 0 15px 0' }}>Role: {node.type} Node</p>
                        
                        <div style={{ fontSize: '14px' }}>
                            <div style={{ marginBottom: '10px' }}>
                                CPU Usage: {node.cpuUsage}%
                                <div style={{ width: '100%', height: '6px', background: '#333', marginTop: '4px', borderRadius: '3px' }}>
                                    <div style={{ width: `${node.cpuUsage}%`, height: '100%', background: '#00a8ff', borderRadius: '3px' }} />
                                </div>
                            </div>
                            <div>
                                RAM Usage: {node.ramUsageGb} GB
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
