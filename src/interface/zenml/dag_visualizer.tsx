import React from 'react';

interface DagNode {
    id: string;
    status: 'completed' | 'running' | 'failed' | 'pending';
}

export const DagVisualizer = ({ nodes }: { nodes: DagNode[] }) => {
    const getStatusColor = (status: string) => {
        switch (status) {
            case 'completed': return '#2ecc71';
            case 'running': return '#f39c12';
            case 'failed': return '#e74c3c';
            default: return '#bdc3c7';
        }
    };

    return (
        <div style={{ display: 'flex', gap: '20px', padding: '20px', alignItems: 'center' }}>
            {nodes.map((node, i) => (
                <React.Fragment key={node.id}>
                    <div style={{ 
                        padding: '10px 20px', 
                        borderRadius: '8px', 
                        backgroundColor: getStatusColor(node.status),
                        color: 'white',
                        fontWeight: 'bold'
                    }}>
                        {node.id}
                    </div>
                    {i < nodes.length - 1 && <span>→</span>}
                </React.Fragment>
            ))}
        </div>
    );
};
