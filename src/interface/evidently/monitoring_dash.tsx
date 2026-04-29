import React from 'react';

interface ModelDrift {
    metric: string;
    driftScore: number;
    isDrifting: boolean;
}

export const EvidentlyDashboard = ({ drifts }: { drifts: ModelDrift[] }) => {
    return (
        <div className="evidently-dash">
            <h2>Model Drift Monitoring</h2>
            <ul>
                {drifts.map(d => (
                    <li key={d.metric} style={{ color: d.isDrifting ? 'red' : 'green' }}>
                        {d.metric}: {d.driftScore.toFixed(3)}
                    </li>
                ))}
            </ul>
        </div>
    );
};
