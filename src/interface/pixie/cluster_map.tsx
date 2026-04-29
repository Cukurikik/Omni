import React from 'react';

export const PixieClusterMap = () => {
    return (
        <div className="pixie-cluster-map">
            <h2>Kubernetes eBPF Traffic Map</h2>
            <svg width="800" height="400">
                <circle cx="200" cy="200" r="40" fill="blue" />
                <circle cx="600" cy="200" r="40" fill="green" />
                <line x1="240" y1="200" x2="560" y2="200" stroke="white" strokeWidth="2" strokeDasharray="5,5" />
                <text x="350" y="190" fill="white">HTTP/gRPC Traffic</text>
            </svg>
        </div>
    );
};
