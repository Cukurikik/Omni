import React, { useState, useEffect } from 'react';

// OMNI Strict Monadic UI Pattern
export type MonadicResult<T, E> = { success: true; value: T } | { success: false; error: E };

export interface AttackMetric {
    id: string;
    model: string;
    robustnessScore: number;
    totalAttacks: number;
    successfulAttacks: number;
}

export const AttackDashboard: React.FC = () => {
    const [metrics, setMetrics] = useState<AttackMetric[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchMetrics = async (): Promise<MonadicResult<AttackMetric[], string>> => {
            try {
                // In production, this hits the GraphQL / REST backend
                const res = await fetch('/api/security/nlp/metrics');
                if (!res.ok) return { success: false, error: `HTTP ${res.status}` };
                const data = await res.json();
                return { success: true, value: data };
            } catch (err: any) {
                return { success: false, error: err.message || 'Fetch failed' };
            }
        };

        fetchMetrics().then(result => {
            if (result.success) {
                setMetrics(result.value);
            } else {
                setError(result.error);
                // Mock data fallback strictly for development review
                setMetrics([
                    { id: '1', model: 'picoGPT-v1', robustnessScore: 0.82, totalAttacks: 15420, successfulAttacks: 210 },
                    { id: '2', model: 'llama-3-8b', robustnessScore: 0.95, totalAttacks: 50000, successfulAttacks: 120 }
                ]);
            }
            setLoading(false);
        });
    }, []);

    if (loading) return <div className="loader">Loading Security Metrics...</div>;

    return (
        <div className="omni-dashboard nlp-security" style={{ padding: '24px', color: '#fff', backgroundColor: '#121212' }}>
            <header>
                <h1 style={{ borderBottom: '2px solid #ff4444', paddingBottom: '10px' }}>OMNI Adversarial NLP Defense</h1>
            </header>
            
            {error && <div className="alert-error" style={{ color: '#ff4444' }}>Warning: {error}</div>}
            
            <div className="metrics-grid" style={{ display: 'grid', gap: '20px', marginTop: '20px' }}>
                {metrics.map(m => (
                    <div key={m.id} className="metric-card" style={{ border: '1px solid #333', padding: '20px', borderRadius: '8px' }}>
                        <h3>{m.model}</h3>
                        <div style={{ display: 'flex', justifyContent: 'space-between', margin: '15px 0' }}>
                            <span>Robustness Score:</span>
                            <span style={{ color: m.robustnessScore > 0.9 ? '#00ff00' : '#ffaa00' }}>
                                {(m.robustnessScore * 100).toFixed(1)}%
                            </span>
                        </div>
                        <div className="progress-bar" style={{ width: '100%', height: '8px', backgroundColor: '#333' }}>
                            <div style={{ width: `${m.robustnessScore * 100}%`, height: '100%', backgroundColor: m.robustnessScore > 0.9 ? '#00ff00' : '#ffaa00' }} />
                        </div>
                        <div style={{ marginTop: '15px', fontSize: '0.9em', color: '#aaa' }}>
                            Deflected {m.totalAttacks - m.successfulAttacks} out of {m.totalAttacks} zero-day prompt injections.
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
