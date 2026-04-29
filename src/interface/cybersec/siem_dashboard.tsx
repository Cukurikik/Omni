import React, { useState, useEffect } from 'react';

export type MonadicResult<T, E> = { success: true; value: T } | { success: false; error: E };

interface SecurityAlert {
    id: string;
    timestamp: Date;
    severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
    sourceIp: string;
    description: string;
}

export const SiemDashboard: React.FC = () => {
    const [alerts, setAlerts] = useState<SecurityAlert[]>([]);
    const [filter, setFilter] = useState<'ALL' | 'CRITICAL' | 'HIGH'>('ALL');

    useEffect(() => {
        // Simulate incoming WebSocket SIEM alerts
        const addAlert = () => {
            const severities: ('CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW')[] = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
            const randomSeverity = severities[Math.floor(Math.random() * severities.length)];
            
            const newAlert: SecurityAlert = {
                id: `ALT-${Math.floor(Math.random() * 10000)}`,
                timestamp: new Date(),
                severity: randomSeverity,
                sourceIp: `192.168.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
                description: randomSeverity === 'CRITICAL' ? 'Potential Data Exfiltration detected' : 
                             randomSeverity === 'HIGH' ? 'Multiple failed login attempts' :
                             'Anomalous network scan activity'
            };

            setAlerts(prev => [newAlert, ...prev].slice(0, 50)); // Keep last 50
        };

        const interval = setInterval(() => {
            if (Math.random() > 0.6) addAlert();
        }, 1500);

        return () => clearInterval(interval);
    }, []);

    const filteredAlerts = alerts.filter(a => filter === 'ALL' || a.severity === filter);

    const getSeverityColor = (sev: string) => {
        switch(sev) {
            case 'CRITICAL': return '#ef4444';
            case 'HIGH': return '#f97316';
            case 'MEDIUM': return '#eab308';
            default: return '#3b82f6';
        }
    };

    return (
        <div style={{ padding: '24px', backgroundColor: '#020617', color: '#f8fafc', minHeight: '100vh', fontFamily: 'Inter, sans-serif' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', borderBottom: '1px solid #1e293b', paddingBottom: '16px' }}>
                <h1 style={{ margin: 0, color: '#38bdf8', fontSize: '1.5rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ width: '12px', height: '12px', backgroundColor: '#ef4444', borderRadius: '50%', display: 'inline-block', boxShadow: '0 0 8px #ef4444' }}></span>
                    Omni Security Operations Center
                </h1>
                
                <div style={{ display: 'flex', gap: '8px' }}>
                    {['ALL', 'CRITICAL', 'HIGH'].map(f => (
                        <button 
                            key={f}
                            onClick={() => setFilter(f as any)}
                            style={{
                                backgroundColor: filter === f ? '#334155' : 'transparent',
                                border: '1px solid #334155',
                                color: filter === f ? '#fff' : '#94a3b8',
                                padding: '6px 12px',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                fontWeight: 'bold',
                                fontSize: '12px'
                            }}
                        >
                            {f}
                        </button>
                    ))}
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
                <div style={{ backgroundColor: '#0f172a', padding: '16px', borderRadius: '8px', borderTop: '4px solid #ef4444' }}>
                    <div style={{ color: '#94a3b8', fontSize: '12px', fontWeight: 'bold' }}>CRITICAL ALERTS (24H)</div>
                    <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{alerts.filter(a => a.severity === 'CRITICAL').length}</div>
                </div>
                <div style={{ backgroundColor: '#0f172a', padding: '16px', borderRadius: '8px', borderTop: '4px solid #f97316' }}>
                    <div style={{ color: '#94a3b8', fontSize: '12px', fontWeight: 'bold' }}>ACTIVE THREATS</div>
                    <div style={{ fontSize: '24px', fontWeight: 'bold' }}>12</div>
                </div>
                <div style={{ backgroundColor: '#0f172a', padding: '16px', borderRadius: '8px', borderTop: '4px solid #3b82f6' }}>
                    <div style={{ color: '#94a3b8', fontSize: '12px', fontWeight: 'bold' }}>EVENTS / SEC</div>
                    <div style={{ fontSize: '24px', fontWeight: 'bold' }}>14,520</div>
                </div>
            </div>

            <div style={{ backgroundColor: '#0f172a', borderRadius: '8px', overflow: 'hidden', border: '1px solid #1e293b' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '14px' }}>
                    <thead style={{ backgroundColor: '#1e293b', color: '#cbd5e1' }}>
                        <tr>
                            <th style={{ padding: '12px 16px' }}>Timestamp</th>
                            <th style={{ padding: '12px 16px' }}>Severity</th>
                            <th style={{ padding: '12px 16px' }}>Source IP</th>
                            <th style={{ padding: '12px 16px' }}>Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredAlerts.length === 0 ? (
                            <tr><td colSpan={4} style={{ padding: '24px', textAlign: 'center', color: '#64748b' }}>No alerts matching filter.</td></tr>
                        ) : filteredAlerts.map(alert => (
                            <tr key={alert.id} style={{ borderBottom: '1px solid #1e293b' }}>
                                <td style={{ padding: '12px 16px', color: '#94a3b8' }}>{alert.timestamp.toLocaleTimeString()}</td>
                                <td style={{ padding: '12px 16px' }}>
                                    <span style={{ 
                                        backgroundColor: getSeverityColor(alert.severity) + '20', 
                                        color: getSeverityColor(alert.severity),
                                        padding: '4px 8px', 
                                        borderRadius: '4px',
                                        fontSize: '11px',
                                        fontWeight: 'bold',
                                        border: `1px solid ${getSeverityColor(alert.severity)}40`
                                    }}>
                                        {alert.severity}
                                    </span>
                                </td>
                                <td style={{ padding: '12px 16px', fontFamily: 'monospace' }}>{alert.sourceIp}</td>
                                <td style={{ padding: '12px 16px', color: '#e2e8f0' }}>{alert.description}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};
