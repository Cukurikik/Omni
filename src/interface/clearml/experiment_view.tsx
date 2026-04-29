import React from 'react';

interface Experiment {
    id: string;
    name: string;
    status: string;
    metrics: Record<string, number>;
}

export const ClearMLExperimentView = ({ experiment }: { experiment: Experiment }) => {
    return (
        <div className="clearml-view" style={{ padding: '20px', background: '#1e1e1e', color: '#fff' }}>
            <h2>Experiment: {experiment.name}</h2>
            <p>Status: <span style={{ color: experiment.status === 'running' ? 'lime' : 'white' }}>{experiment.status}</span></p>
            <div className="metrics">
                {Object.entries(experiment.metrics).map(([key, val]) => (
                    <div key={key}><strong>{key}</strong>: {val.toFixed(4)}</div>
                ))}
            </div>
        </div>
    );
};
