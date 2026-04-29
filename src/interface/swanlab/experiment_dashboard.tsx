import React, { useState, useEffect } from 'react';

// OMNI SWANLAB: Experiment Dashboard
// React TSX UI for tracking ML training runs, comparing hyperparameters, and viewing loss curves.
// Source: SwanHubX/SwanLab

interface ExperimentRun {
    id: string;
    name: string;
    status: 'RUNNING' | 'COMPLETED' | 'FAILED';
    metrics: { loss: number; accuracy: number };
    hyperparams: { lr: number; batch_size: number };
    duration: string;
}

export const ExperimentDashboard: React.FC = () => {
    const [runs, setRuns] = useState<ExperimentRun[]>([
        { id: "run-001", name: "resnet-lr-0.01", status: "COMPLETED", metrics: { loss: 0.23, accuracy: 94.5 }, hyperparams: { lr: 0.01, batch_size: 128 }, duration: "4h 23m" },
        { id: "run-002", name: "resnet-lr-0.001", status: "RUNNING", metrics: { loss: 0.45, accuracy: 89.2 }, hyperparams: { lr: 0.001, batch_size: 128 }, duration: "1h 10m" },
        { id: "run-003", name: "resnet-bs-256", status: "FAILED", metrics: { loss: 1.89, accuracy: 32.1 }, hyperparams: { lr: 0.01, batch_size: 256 }, duration: "14m" },
    ]);

    return (
        <div style={{ padding: '24px', fontFamily: 'Inter, system-ui', backgroundColor: '#f9fafb', minHeight: '100vh', color: '#111827' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                <h1 style={{ fontSize: '24px', fontWeight: 600, margin: 0 }}>SwanLab Dashboard</h1>
                <button style={{ backgroundColor: '#2563eb', color: '#fff', border: 'none', padding: '8px 16px', borderRadius: '6px', cursor: 'pointer', fontWeight: 500 }}>
                    + New Project
                </button>
            </div>

            <div style={{ backgroundColor: '#fff', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                    <thead style={{ backgroundColor: '#f3f4f6', borderBottom: '1px solid #e5e7eb' }}>
                        <tr>
                            <th style={{ padding: '12px 16px', fontWeight: 500, color: '#4b5563' }}>Run Name</th>
                            <th style={{ padding: '12px 16px', fontWeight: 500, color: '#4b5563' }}>Status</th>
                            <th style={{ padding: '12px 16px', fontWeight: 500, color: '#4b5563' }}>Loss</th>
                            <th style={{ padding: '12px 16px', fontWeight: 500, color: '#4b5563' }}>Accuracy</th>
                            <th style={{ padding: '12px 16px', fontWeight: 500, color: '#4b5563' }}>LR</th>
                            <th style={{ padding: '12px 16px', fontWeight: 500, color: '#4b5563' }}>Batch Size</th>
                            <th style={{ padding: '12px 16px', fontWeight: 500, color: '#4b5563' }}>Duration</th>
                        </tr>
                    </thead>
                    <tbody>
                        {runs.map((run, idx) => (
                            <tr key={run.id} style={{ borderBottom: idx === runs.length - 1 ? 'none' : '1px solid #e5e7eb' }}>
                                <td style={{ padding: '12px 16px', fontWeight: 500, color: '#2563eb' }}>{run.name}</td>
                                <td style={{ padding: '12px 16px' }}>
                                    <span style={{ 
                                        padding: '4px 8px', borderRadius: '9999px', fontSize: '12px', fontWeight: 500,
                                        backgroundColor: run.status === 'COMPLETED' ? '#dcfce7' : run.status === 'RUNNING' ? '#dbeafe' : '#fee2e2',
                                        color: run.status === 'COMPLETED' ? '#166534' : run.status === 'RUNNING' ? '#1e40af' : '#991b1b'
                                    }}>
                                        {run.status}
                                    </span>
                                </td>
                                <td style={{ padding: '12px 16px', fontFamily: 'monospace' }}>{run.metrics.loss.toFixed(4)}</td>
                                <td style={{ padding: '12px 16px' }}>{run.metrics.accuracy}%</td>
                                <td style={{ padding: '12px 16px' }}>{run.hyperparams.lr}</td>
                                <td style={{ padding: '12px 16px' }}>{run.hyperparams.batch_size}</td>
                                <td style={{ padding: '12px 16px', color: '#6b7280' }}>{run.duration}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};
