import React from 'react';
import { MetricChart } from './metric_chart';

export const AimDashboard = ({ runs }: { runs: any[] }) => {
    return (
        <div style={{ padding: '20px', fontFamily: 'Inter, sans-serif' }}>
            <header style={{ borderBottom: '1px solid #eee', paddingBottom: '10px' }}>
                <h2>Aim Experiment Tracker</h2>
                <p>Tracking {runs.length} Active Runs</p>
            </header>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginTop: '20px' }}>
                <MetricChart metricName="Loss" data={runs.map(r => r.metrics.loss)} />
                <MetricChart metricName="Accuracy" data={runs.map(r => r.metrics.accuracy)} />
            </div>
        </div>
    );
};
