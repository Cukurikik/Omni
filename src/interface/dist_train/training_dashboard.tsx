import React, { useState, useEffect } from 'react';

export type MonadicResult<T, E> = { success: true; value: T } | { success: false; error: E };

interface TrainingMetrics {
    epoch: number;
    loss: number;
    throughput: number; // samples per second
    activeNodes: number;
}

export const TrainingDashboard: React.FC = () => {
    const [metrics, setMetrics] = useState<TrainingMetrics | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [isRunning, setIsRunning] = useState(false);

    useEffect(() => {
        if (!isRunning) return;

        let epoch = 0;
        let loss = 2.5;

        const interval = setInterval(() => {
            epoch += 1;
            loss = loss * 0.95; // Simulating convergence

            if (epoch > 100) {
                setIsRunning(false);
                clearInterval(interval);
            } else {
                setMetrics({
                    epoch,
                    loss,
                    throughput: 450 + Math.random() * 50,
                    activeNodes: 8
                });
            }
        }, 1000);

        return () => clearInterval(interval);
    }, [isRunning]);

    return (
        <div style={{ padding: '24px', backgroundColor: '#0f172a', color: '#f1f5f9', minHeight: '100vh', fontFamily: 'system-ui, sans-serif' }}>
            <h1 style={{ color: '#38bdf8', marginBottom: '8px' }}>Distributed Training Cluster</h1>
            <p style={{ color: '#94a3b8', marginBottom: '24px' }}>Alpa / NCCL Acceleration Enabled</p>

            <button 
                onClick={() => setIsRunning(!isRunning)}
                style={{
                    backgroundColor: isRunning ? '#ef4444' : '#10b981',
                    color: 'white',
                    border: 'none',
                    padding: '10px 20px',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontWeight: 'bold',
                    marginBottom: '24px'
                }}
            >
                {isRunning ? 'Stop Training' : 'Start Training'}
            </button>

            {error && <div style={{ color: '#ef4444', padding: '12px', border: '1px solid #ef4444', borderRadius: '4px', marginBottom: '24px' }}>{error}</div>}

            {metrics && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                    <MetricCard title="Epoch" value={metrics.epoch.toString()} />
                    <MetricCard title="Current Loss" value={metrics.loss.toFixed(4)} />
                    <MetricCard title="Throughput" value={`${metrics.throughput.toFixed(0)} samples/s`} />
                    <MetricCard title="Active Nodes" value={metrics.activeNodes.toString()} />
                </div>
            )}
            
            {metrics && (
                <div style={{ marginTop: '32px', backgroundColor: '#1e293b', padding: '16px', borderRadius: '8px' }}>
                    <h3 style={{ margin: '0 0 16px 0', color: '#cbd5e1' }}>Loss Curve</h3>
                    <div style={{ width: '100%', height: '100px', backgroundColor: '#0f172a', position: 'relative', overflow: 'hidden' }}>
                        {/* Visual indicator of progress */}
                        <div style={{ 
                            position: 'absolute', 
                            bottom: 0, 
                            left: 0, 
                            height: `${(2.5 - metrics.loss) / 2.5 * 100}%`, 
                            width: `${metrics.epoch}%`,
                            backgroundColor: '#38bdf8',
                            transition: 'all 0.5s ease'
                        }} />
                    </div>
                </div>
            )}
        </div>
    );
};

const MetricCard: React.FC<{title: string, value: string}> = ({title, value}) => (
    <div style={{ backgroundColor: '#1e293b', padding: '20px', borderRadius: '8px', borderLeft: '4px solid #38bdf8' }}>
        <div style={{ fontSize: '0.875rem', color: '#94a3b8', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{title}</div>
        <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#f8fafc' }}>{value}</div>
    </div>
);
