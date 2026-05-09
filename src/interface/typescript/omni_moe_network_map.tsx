import React from 'react';

// OMNI MOTHER: Interactive Network Map for MoE Topology

export const OmniNetworkMap: React.FC = () => {
    return (
        <div style={{ padding: '20px', border: '1px solid #ccc' }}>
            <h3>Cluster Topology</h3>
            <svg width="400" height="200">
                <circle cx="50" cy="100" r="20" fill="#3b82f6" />
                <circle cx="350" cy="100" r="20" fill="#10b981" />
                <line x1="70" y1="100" x2="330" y2="100" stroke="#94a3b8" strokeWidth="2" strokeDasharray="5,5" />
                <text x="160" y="90" fill="#94a3b8">gRPC Stream</text>
            </svg>
        </div>
    );
};
