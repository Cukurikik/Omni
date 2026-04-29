import React from 'react';

export const TrainingMonitor: React.FC = () => {
    return (
        <div className="monitor">
            <h2>Catalyst Monitor</h2>
            <div className="progress">Epoch 45 / 100</div>
            <div className="loss">Current Loss: 0.0452</div>
        </div>
    );
};
