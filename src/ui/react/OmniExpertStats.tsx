import React from 'react';

// OMNI MOTHER: React component for high-level cluster stats.

interface Props {
    totalTokens: number;
    imbalanceFactor: number;
    avgLatency: number;
}

export const OmniExpertStats: React.FC<Props> = ({ totalTokens, imbalanceFactor, avgLatency }) => {
    return (
        <div className="omni-expert-stats">
            <div className="stat-box">
                <span className="stat-label">Total Tokens</span>
                <span className="stat-value">{totalTokens.toLocaleString()}</span>
            </div>
            <div className="stat-box">
                <span className="stat-label">Load Imbalance Factor</span>
                <span className="stat-value">{imbalanceFactor.toFixed(3)}</span>
            </div>
            <div className="stat-box">
                <span className="stat-label">Avg Routing Latency</span>
                <span className="stat-value">{avgLatency.toFixed(2)} ms</span>
            </div>
        </div>
    );
};
